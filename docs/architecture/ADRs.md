# Architecture Decision Records (ADRs) - Proyecto CleanPro

Este documento registra las decisiones arquitectónicas y técnicas tomadas por el **Equipo 12** para el diseño, implementación y despliegue de la solución de software de **CleanPro**.

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
  * **Positivas:** Imposibilidad de instanciar o persistir estados inválidos; alta cohesión; trazabilidad directa 1 a 1 con el glosario de lenguaje ubicuo y pruebas unitarias ultrarrápidas sin acoplamiento a infraestructura.
  * **Negativas:** Mayor esfuerzo de modelado inicial para definir límites de agregados y objetos de valor en comparación con un script directo.

---

## ADR-002: Implementación de State Machine para el Ciclo de Vida de Cotizaciones y Órdenes de Servicio

* **Estado:** Aceptado
* **Fecha:** 20 de octubre de 2026
* **Contexto:**  
  Los criterios de aceptación exigen restricciones secuenciales estrictas: una cotización con descuento mayor al 10% no puede enviarse ni aceptarse mientras esté pendiente de autorización (CA-04.2); una cotización aceptada no puede editarse (CA-05.4); una orden de servicio no puede cerrarse si antes no se registró su hora de inicio (CA-09.2); y sólo los servicios cerrados o con cargo por penalización pueden pasar a facturación (CA-18.1).
* **Decisión:**  
  Implementar el patrón **State Machine (Máquina de Estados Finitos)** mediante las clases `CotizacionStateMachine` y `OrdenServicioStateMachine` (`src/domain/state_machines.py`), utilizando enumeraciones tipadas (`EstadoCotizacion`, `EstadoOrdenServicio`) y grafos explícitos de transiciones permitidas que lanzan `DomainError` ante cualquier transición ilegal.
* **Alternativas Consideradas:**
  1. *Atributos booleanos múltiples (`is_authorized`, `is_sent`, `is_accepted`, `is_closed`):* Se descartó porque permite combinaciones contradictorias (ej. `is_accepted=True` con `is_authorized=False`).
  2. *Mutación libre de cadenas de texto (`orden.estado = "Cerrado"`):* Se descartó por carecer de protección contra saltos de flujo (como cerrar un servicio sin haberlo iniciado).
* **Consecuencias:**
  * **Positivas:** Garantía total de que ninguna entidad salte etapas obligatorias del proceso BPMN; mensajes de error claros y auditables para la capa REST.
  * **Negativas:** Cualquier nuevo estado futuro requiere actualizar explícitamente la matriz de transiciones y sus pruebas unitarias.

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
  2. *Motor de reglas externo (ej. Drools):* Se descartó por introducir una complejidad de infraestructura excesiva para las 9 reglas del dominio CleanPro.
* **Consecuencias:**
  * **Positivas:** Cumplimiento estricto del principio Abierto/Cerrado (OCP) y de *12-Factor App*; facilidad para probar cada regla de negocio en aislamiento con valores límite (*boundary testing*).
  * **Negativas:** Incremento moderado en la cantidad de clases dentro de la capa de dominio.

  ---

## ADR-004: Stack Tecnológico (Python 3.11 + FastAPI + Pytest + Docker Compose)

* **Estado:** Aceptado
* **Fecha:** 28 de octubre de 2026
* **Contexto:**  
  El PIA requiere una API REST funcional con especificación OpenAPI/Swagger UI activa en producción, una suite de pruebas automatizadas (unitarias y de integración) con cobertura mínima del 80%, un pipeline CI/CD en GitHub Actions y un entorno contenerizado reproducible con Docker Compose (`DB + App + Tests`).
* **Decisión:**  
  Utilizar **Python 3.11** con **FastAPI** para la capa REST y generación automática de OpenAPI 3.0 (`/docs`), **SQLAlchemy / Repositorio desacoplado** para persistencia, **Pytest + pytest-cov** para la suite de pruebas y **Docker Compose** orquestando PostgreSQL 15, el contenedor de la aplicación y el contenedor de pruebas.
* **Alternativas Consideradas:**
  1. *Express.js (Node.js):* Se descartó porque la generación y mantenimiento de esquemas OpenAPI/Swagger requiere configuración manual adicional propensa a desincronizarse del código.
  2. *Spring Boot (Java):* Se descartó por tiempos de compilación más lentos en CI/CD y mayor consumo de memoria RAM en plataformas gratuitas de despliegue en la nube (Render / Railway / Fly.io).
* **Consecuencias:**
  * **Positivas:** Documentación interactiva Swagger UI generada directamente desde los DTOs de Pydantic; ejecución completa de la suite de pruebas con más del 90% de cobertura en menos de 2 segundos; despliegue inmediato mediante `Dockerfile` ligero (`python:3.11-slim`).
  * **Negativas:** Requiere validación estricta de tipos con Pydantic y `dataclasses` para mantener la seguridad de tipos en tiempo de ejecución.