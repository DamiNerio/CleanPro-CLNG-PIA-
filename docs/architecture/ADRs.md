# Architecture Decision Records (ADRs) - Proyecto CleanPro

Este documento registra las decisiones arquitectónicas y técnicas tomadas por el **Equipo 12** para el diseño, implementación, separación de interfaces y despliegue en producción de la solución de software de **CleanPro**.

---

## ADR-001: Uso del Patrón Domain Model (DDD) sobre Transaction Script

* **Estado:** Aceptado
* **Fecha:** 13 de octubre de 2026
* **Contexto:**  
  El sistema CleanPro necesita gestionar el flujo completo desde la solicitud de cotización hasta la ejecución en sitio y su facturación. Durante el levantamiento de requerimientos se identificaron 9 reglas de negocio estrictas (RN-01 a RN-09), incluyendo límites jerárquicos para descuentos (hasta 10% coordinador vs. mayor a 10% gerencia), topes de superficie (300 m2) y monto ($8,000 MXN), cargos por cancelación tardía (50%) y acceso denegado (100%), así como validaciones de evidencia fotográfica obligatoria.
* **Decisión:**  
  Implementar el patrón **Domain Model (Modelo de Dominio)** siguiendo **Domain-Driven Design (DDD)**, encapsulando toda la lógica e invariantes dentro de Raíces de Agregado (`CotizacionFormal`, `OrdenDeServicio`), Entidades (`Cuadrilla`, `Incidencia`, `ServicioExtra`) y Objetos de Valor inmutables (`Monto`, `Superficie`, `Descuento`, `FirmaConformidad`), apoyados por un *Service Layer* dedicado exclusivamente a la orquestación de casos de uso.
* **Alternativas Consideradas:**
  1. *Transaction Script:* Organizar la lógica en funciones procedurales dentro de los endpoints REST. Se descartó porque provoca duplicación de validaciones y alto riesgo de dejar entidades en estados inconsistentes.
  2. *Active Record:* Acoplar directamente las reglas de negocio a las tablas del ORM. Se descartó por dificultar las pruebas unitarias aisladas y violar el principio de responsabilidad única (SRP).
* **Consecuencias:**
  * **Positivas:** Imposibilidad de instanciar o persistir estados inválidos; alta cohesión; trazabilidad directa 1 a 1 con el glosario de lenguaje ubicuo y pruebas unitarias rápidas sin acoplamiento a infraestructura.
  * **Negativas:** Mayor esfuerzo de modelado inicial para definir límites de agregados y objetos de valor en comparación con un script directo.

---

## ADR-002: Implementación de State Machine para el Ciclo de Vida de Cotizaciones y Órdenes de Servicio

* **Estado:** Aceptado y Refinado
* **Fecha:** 20 de octubre de 2026 (Refinado el 4 de noviembre de 2026)
* **Contexto:**  
  Los criterios de aceptación exigen restricciones secuenciales estrictas: una cotización dentro de los límites del coordinador puede ser aceptada por el cliente, pero si tiene un descuento mayor al 10% o supera 300 m2 / $8,000 queda bloqueada en `Pendiente de autorización` hasta que Gerencia la apruebe (CA-04.2); una cotización aceptada es inmutable (CA-05.4); una orden de servicio generada debe pasar obligatoriamente por `Programada` antes de pasar a `En ejecución`, y no puede cerrarse sin haber registrado su hora de inicio (CA-09.2).
* **Decisión:**  
  Implementar el patrón **State Machine (Máquina de Estados Finitos)** mediante las clases `CotizacionStateMachine` y `OrdenServicioStateMachine` (`src/domain/state_machines.py`), utilizando enumeraciones tipadas (`EstadoCotizacion`, `EstadoOrdenServicio`) y tablas explícitas de transiciones permitidas que lanzan `DomainError` ante cualquier transición ilegal.
* **Alternativas Consideradas:**
  1. *Atributos booleanos múltiples (`is_authorized`, `is_sent`, `is_accepted`, `is_closed`):* Se descartó porque permite combinaciones contradictorias.
  2. *Mutación libre de cadenas de texto (`orden.estado = "Cerrado"`):* Se descartó por carecer de protección contra saltos de flujo (como iniciar un servicio sin programarlo o cerrarlo sin iniciarlo).
* **Consecuencias:**
  * **Positivas:** Garantía total de que ninguna entidad salte etapas obligatorias del proceso BPMN; mensajes de error claros y auditables tanto en la API como en los portales web.
  * **Negativas:** Las pruebas automatizadas deben seguir rigurosamente la secuencia de estados del negocio (ej. programar antes de iniciar).

---

## ADR-003: Uso del Patrón Specification Parametrizado con Variables de Entorno (12-Factor App)

* **Estado:** Aceptado
* **Fecha:** 24 de octubre de 2026
* **Contexto:**  
  El BRD establece que todas las cifras operativas obtenidas en el levantamiento (10% de descuento, 300 m2, $8,000 MXN, rendimiento de 60 m2/h, 24 horas de anticipación para cancelación y máximo 2 reprogramaciones al mes) deben manejarse como parámetros configurables sin requerir cambios de programación (CA-02.2), cumpliendo además con la metodología *12-Factor App*.
* **Decisión:**  
  Implementar el patrón **Specification** (`src/domain/specifications.py`) mediante clases especializadas (`DescuentoAutorizablePorCoordinadorSpec`, `CotizacionDentroDeLimiteCoordinadorSpec`, `CancelacionSinPenalizacionSpec`, `ClienteSuperaLimiteReprogramacionesSpec`, `CuadrillaDisponibleSpec`) cuyos umbrales por defecto se inyectan desde variables de entorno leídas en `src/infrastructure/config.py`.
* **Alternativas Consideradas:**
  1. *Constantes fijas (hardcoded) dentro de los métodos de las entidades:* Se descartó porque incumple el criterio CA-02.2 y obliga a modificar código fuente si la gerencia cambia un umbral.
  2. *Motor de reglas externo:* Se descartó por introducir una complejidad de infraestructura innecesaria para las 9 reglas del dominio CleanPro.
* **Consecuencias:**
  * **Positivas:** Cumplimiento estricto del principio Abierto/Cerrado (OCP) y de *12-Factor App*; facilidad para probar cada regla de negocio en aislamiento.
  * **Negativas:** Incremento moderado en la cantidad de clases dentro de la capa de dominio.

---

## ADR-004: Stack Tecnológico y Configuración de Despliegue en Render (`PYTHON_VERSION=3.11.9`)

* **Estado:** Aceptado
* **Fecha:** 4 de noviembre de 2026
* **Contexto:**  
  El PIA requiere una API REST funcional con especificación OpenAPI/Swagger UI activa en producción, una suite de pruebas automatizadas con cobertura mínima del 80%, un pipeline CI/CD en GitHub Actions, un entorno reproducible con Docker Compose (`DB + App + Tests`) y un despliegue funcional en la nube (Render). Durante el despliegue en Render, las versiones experimentales de Python por defecto intentaban compilar extensiones de Rust (`pydantic-core` vía `maturin`/`cargo`) en un sistema de archivos de solo lectura (`os error 30`).
* **Decisión:**  
  Utilizar **Python 3.11** (`PYTHON_VERSION=3.11.9` en las variables de entorno de Render y `python:3.11-slim` en Docker) junto con **FastAPI**, **Uvicorn**, **Pydantic**, **Pytest + pytest-cov** y **Docker Compose**.
* **Alternativas Consideradas:**
  1. *Compilar paquetes desde código fuente en el contenedor de Render:* Se descartó por el bloqueo de sistema de archivos de solo lectura en el registro de Cargo y mayores tiempos de despliegue.
  2. *Express.js / Spring Boot:* Se descartaron por requerir configuración adicional de Swagger o mayor consumo de memoria RAM en capas gratuitas de nube.
* **Consecuencias:**
  * **Positivas:** Descarga inmediata de paquetes binarios precompilados (*wheels*) en Render y GitHub Actions; compuerta de cobertura mínima del 80% aplicada en cada push por GitHub Actions; Swagger UI activo en `/docs`.
  * **Negativas:** Se debe declarar explícitamente la variable `PYTHON_VERSION=3.11.9` al configurar el entorno en Render.

---

## ADR-005: Separación de Interfaces Web por Rol (Portal Público del Cliente `/` vs. Intranet Administrativa `/admin`)

* **Estado:** Aceptado
* **Fecha:** 4 de noviembre de 2026
* **Contexto:**  
  El inspector técnico Swagger UI (`/docs`) expone formatos JSON y terminología de programación que resultan poco intuitivos para un cliente final. Además, por privacidad y seguridad operativa del negocio, un cliente externo de CleanPro nunca debe visualizar ni tener acceso a los controles internos del Coordinador, la bitácora del Supervisor, las autorizaciones de Gerencia, los registros de Nómina ni la bandeja de Facturación.
* **Decisión:**  
  Construir e integrar dos aplicaciones web gráficas independientes servidas por FastAPI sobre la misma API REST:
  1. **Portal Público del Cliente (`GET /` -> `src/api/index.html`):** Interfaz comercial limpia donde el cliente únicamente solicita su cotización, consulta su estado, acepta la propuesta, cancela su cita o firma digitalmente de conformidad/inconformidad.
  2. **Intranet Operativa y Administrativa (`GET /admin` -> `src/api/admin.html`):** Panel corporativo interno dividido en pestañas para Coordinador, Supervisor en Sitio y Gerencia/Administración, manteniendo además el enlace técnico a Swagger UI (`/docs`).
* **Alternativas Consideradas:**
  1. *Dejar únicamente Swagger UI (`/docs`) para todos los usuarios:* Se descartó porque un cliente real no comprende esquemas JSON ni códigos HTTP.
  2. *Un solo panel web unificado con todas las pestañas mezcladas:* Se descartó porque expone información administrativa sensible (nómina, facturación, descuentos internos) a la vista del cliente.
* **Consecuencias:**
  * **Positivas:** Separación clara de responsabilidades y privacidad de negocio; experiencia de usuario intuitiva sin jerga técnica; facilita enormemente la demostración en vivo durante la defensa del PIA.
  * **Negativas:** Requiere mantener sincronizados dos archivos HTML (`index.html` y `admin.html`) dentro del paquete `src/api/`.

---

## ADR-006: Persistencia Relacional con SQLAlchemy detrás de un Puerto de Repositorio

* **Estado:** Aceptado (reemplaza el repositorio en memoria usado hasta la v1.0)
* **Fecha:** 6 de noviembre de 2026
* **Contexto:**  
  La primera versión guardaba cotizaciones y órdenes en diccionarios de Python. Los datos se perdían en cada reinicio (Render apaga el servicio gratuito tras unos minutos sin uso), el contenedor PostgreSQL de Docker Compose no se usaba y la clase de repositorio estaba duplicada en `application/` e `infrastructure/`, rompiendo la separación de capas. Además, el problema principal del negocio (servicios sin facturar, cambios de nómina que se pierden) exige que esos registros sean persistentes.
* **Decisión:**
  1. Definir el puerto abstracto `RepositorioCleanPro` en `src/domain/repositories.py`; los servicios de aplicación dependen solo de él.
  2. Implementar `RepositorioSQLAlchemy` (SQLAlchemy 2.0 Core) en `src/infrastructure/sqlalchemy_repository.py`, compatible con **SQLite** (local, CI) y **PostgreSQL** (Docker Compose, Render), elegido con `DATABASE_URL`.
  3. Guardar cada agregado en su tabla: las columnas por las que se consulta (estado, cliente, cuadrilla, fecha programada, total) son columnas reales; el detalle interno del agregado (incidencias, extras, firma, descuento) se guarda en una columna `JSON` mediante `mappers.py`. Registros facturables y cambios de personal son tablas totalmente relacionales.
  4. Conservar `RepositorioEnMemoria` (también serializa con los mappers) para pruebas unitarias rápidas.
* **Alternativas Consideradas:**
  1. *ORM completo con una tabla por entidad interna (incidencias, extras, firmas):* más normalizado, pero obliga a mapear cada cambio del modelo y a manejar migraciones; desproporcionado para el alcance del PIA.
  2. *Seguir en memoria:* descartado porque pierde datos y no cumple el requisito "DB + App + Tests".
  3. *Agregar Alembic para migraciones:* se pospone; con `metadata.create_all()` basta mientras el esquema sea nuevo.
* **Consecuencias:**
  * **Positivas:** Los datos sobreviven reinicios; el mismo código corre en SQLite y PostgreSQL; el dominio no conoce la base de datos (DIP); las pruebas de contrato (`tests/test_repositories.py`) demuestran que ambos adaptadores son intercambiables.
  * **Negativas:** Consultar por campos internos del JSON (p. ej. tipo de incidencia) requiere leer el agregado completo; un cambio de esquema futuro requerirá introducir migraciones.

---

## ADR-007: Excepciones de Dominio Tipadas y Traducción Centralizada a Códigos HTTP

* **Estado:** Aceptado
* **Fecha:** 6 de noviembre de 2026
* **Contexto:**  
  Varios endpoints devolvían `500 Internal Server Error` ante folios inexistentes o reglas violadas, y cada controlador decidía su propio código con `try/except`, duplicando lógica.
* **Decisión:**  
  Crear `src/domain/exceptions.py` con `DomainError`, `TransicionInvalida`, `ConflictoDeAgenda` y `AutorizacionRequerida`, y `RecursoNoEncontrado` en la capa de aplicación. `src/api/main.py` registra un único manejador que traduce: 404 recurso inexistente · 403 requiere gerencia (RN-01/RN-02) · 409 transición inválida o traslape de agenda · 422 dato o regla inválida.
* **Alternativas Consideradas:** Mantener `try/except` en cada endpoint (código repetido y fácil de olvidar); usar un solo código 400 para todo (el cliente no distingue el tipo de problema).
* **Consecuencias:**
  * **Positivas:** Controladores delgados; respuestas consistentes `{"detail", "tipo"}` que el portal y la intranet muestran al usuario; ningún error de negocio produce 500.
  * **Negativas:** Cada nueva excepción de dominio debe ubicarse en la jerarquía correcta.

---

## ADR-008: El Portal del Cliente solo muestra las solicitudes del propio cliente

* **Estado:** Aceptado (complementa ADR-005)
* **Fecha:** 6 de noviembre de 2026
* **Contexto:**  
  En la revisión de la Unidad 4 el profesor, actuando como cliente, señaló que un cliente no entiende interfaces técnicas. El portal `/` resolvió eso, pero consultaba `/api/estado`, que devuelve las cotizaciones de todos los clientes junto con nómina y facturación.
* **Decisión:**  
  Introducir la entidad `Cliente`, identificada por su teléfono o correo normalizado, y el endpoint `GET /api/clientes/solicitudes?contacto=...`. El portal recuerda el contacto con el que se pidió la cotización y solo muestra esas solicitudes, con los estados traducidos a lenguaje del cliente ("Agendado", "Nuestro equipo está trabajando", "Cancelado sin costo"). `/api/estado` queda para la intranet.
* **Alternativas Consideradas:** Cuentas con usuario y contraseña (fuera del alcance del BRD); mostrar todo (expone datos de otros clientes).
* **Consecuencias:**
  * **Positivas:** Privacidad entre clientes; lenguaje comprensible para el cliente; la demostración puede hacerse con el profesor como cliente.
  * **Negativas:** Identificar por contacto no es autenticación: quien conozca el teléfono de otro cliente podría consultarlo. Para producción real se recomienda agregar un código enviado por correo o SMS.

