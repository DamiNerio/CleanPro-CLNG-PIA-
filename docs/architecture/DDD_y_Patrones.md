# Arquitectura de Software: Modelo DDD, Patrones de Diseño y Principios SOLID

## 1. Justificación del Patrón de Lógica de Negocio: Domain Model vs. Transaction Script

Para el sistema de gestión de **CleanPro**, se seleccionó el patrón **Domain Model (Modelo de Dominio)** bajo el enfoque de **Domain-Driven Design (DDD)** en lugar de un *Transaction Script*.

CleanPro opera con invariantes de negocio estrictas y ciclos de vida complejos: bloqueo de descuentos mayores al 10% sin visto bueno de gerencia (RN-01), límites operativos de 300 m2 u $8,000 MXN para el coordinador (RN-02), penalizaciones diferenciadas del 50% por cancelación tardía (RN-04) y del 100% por acceso denegado (RN-05), y validación obligatoria de evidencias fotográficas antes del cierre (US-10, US-15). Un *Transaction Script* dispersaría estas validaciones en controladores o procedimientos secuenciales, provocando duplicidad de código y riesgo de estados corruptos. El *Domain Model* encapsula estas invariantes dentro de las propias Raíces de Agregado (`CotizacionFormal` y `OrdenDeServicio`), garantizando que ninguna entidad pueda existir ni persistirse en un estado inválido.

### Tabla Comparativa de Arquitectura

| Característica | Transaction Script | Domain Model (Seleccionado) | Beneficio Directo en CleanPro |
| :--- | :--- | :--- | :--- |
| **Estructura** | Lógica agrupada en un solo procedimiento por acción (ej. `script_generar_cotizacion`). | Lógica distribuida en objetos ricos que representan conceptos reales del dominio (Agregados, Entidades, Value Objects). | Modela fielmente los conceptos descubiertos en el levantamiento (`CotizacionFormal`, `OrdenDeServicio`, `Cuadrilla`, `Incidencia`). |
| **Manejo de Reglas** | Condicionales `if/else` dispersos en la capa de interfaz o controladores HTTP. | Las invariantes y especificaciones viven dentro de los objetos del dominio (`src/domain/`). | Impide aprobar un descuento del 15% o cotizar 400 m2 sin pasar por el estado `Pendiente de autorización`. |
| **Control de Estados** | Los estados se sobrescriben modificando columnas de texto directamente en la base de datos. | Una Máquina de Estados (`State Machine`) interna controla qué transiciones son legales desde cada etapa. | Garantiza que ningún servicio pase a `En ejecución` si no fue `Programada`, ni pase a `Cerrado con conformidad` sin haber iniciado. |
| **Mantenibilidad** | Alta fragilidad al agregar nuevas políticas (código espagueti). | Si cambia una política comercial, sólo se modifica la especificación o entidad responsable. | Permite ajustar umbrales (m2, porcentajes, horas de cancelación) sin romper los servicios de aplicación ni las vistas HTML. |

---

## 2. Mapa de Dominio Táctico (Elementos DDD)

### 2.1 Aggregate Roots (Raíces de Agregado)
1. **`CotizacionFormal` (`src/domain/entities.py`):**
   * Raíz de agregado de la fase comercial (pre-venta).
   * **Invariantes que protege:** Cálculo automático de horas-persona y tamaño de cuadrilla según el rendimiento configurable (US-02); restricción de descuentos mayores al 10% y límites de 300 m2 / $8,000 exigiendo transición inmediata a `Pendiente de autorización` (RN-01, RN-02); bloqueo de envío o aceptación por el cliente mientras esté pendiente de autorización (CA-04.2); inmutabilidad una vez que alcanza el estado `Aceptada` (CA-05.4); generación automática de `OrdenDeServicio` al aceptarse (RN-09).
2. **`OrdenDeServicio` (`src/domain/entities.py`):**
   * Raíz de agregado de la fase operativa y post-venta.
   * **Invariantes que protege:** Orquesta y protege a las entidades internas (`Cuadrilla`, `Incidencia`, `ServicioExtra`, `FirmaConformidad`); exige estar en estado `Programada` antes de poder iniciar (`En ejecución`) e impide registrar término sin marca de inicio previa (CA-09.2); bloquea el cierre si alguna incidencia carece de descripción o fotografía (CA-10.4); exige evidencia fotográfica para recálculo proporcional de superficie (RN-07) o acceso denegado (RN-05); calcula automáticamente el monto facturable al 100% o 50% según la regla aplicable.

### 2.2 Entities (Entidades)
* **`Cuadrilla`:** Posee identidad única (`C-03`, `C-05`, `C-07`), lista de integrantes activos y registro de ventanas de tiempo asignadas para impedir traslapes de horario.
* **`Incidencia`:** Representa un percance en sitio asociado a una orden; contiene tipo, descripción, lista de fotografías y marca de tiempo.
* **`ServicioExtra`:** Representa un trabajo adicional solicitado en el domicilio con descripción, costo y estado de autorización del cliente.

### 2.3 Value Objects (Objetos de Valor Inmutables - `src/domain/value_objects.py`)
* **`Monto`:** Representa valores monetarios (subtotales, totales, extras y penalizaciones). Su invariante prohíbe valores negativos (< 0) y provee operaciones inmutables de descuento porcentual y factor proporcional.
* **`Superficie`:** Representa el metraje del inmueble en m2. Su invariante exige que sea estrictamente mayor a cero (> 0, CA-01.3).
* **`Descuento`:** Encapsula el porcentaje (0% a 100%), el motivo comercial y el usuario que lo solicita.
* **`FirmaConformidad`:** Objeto inmutable del Acta Digital que encapsula el nombre del firmante, el booleano de conformidad, la fecha/hora y valida que, en caso de inconformidad, el motivo no esté vacío (CA-11.3).

### 2.4 Domain Events (Eventos de Dominio - `src/domain/events.py`)
* **`CotizacionAceptada`:** Emitido cuando el cliente acepta la propuesta; detona la creación de la `OrdenDeServicio` (RN-09).
* **`AusenciaReportada`:** Emitido cuando el supervisor reporta la falta de un integrante; detona la creación inmediata del registro estructurado para nómina en Administración (US-12, US-17).
* **`AccesoDenegadoRegistrado`:** Emitido cuando el cliente impide el acceso en sitio; detona la liberación de la cuadrilla y el registro facturable al 100% (RN-05, US-13).
* **`ServicioCerrado`:** Emitido al capturar la firma digital del cliente; detona la creación del registro facturable por el total de la orden más extras autorizados (RN-09, US-18).

---

## 3. Patrones de Diseño Obligatorios del Curso

### 3.1 Patrón Specification (`src/domain/specifications.py`)
El patrón **Specification** encapsula reglas de negocio booleanas en clases independientes que implementan la interfaz `Specification[T].is_satisfied_by(candidate) -> bool`:

1. **`DescuentoAutorizablePorCoordinadorSpec` (RN-01):** Evalúa si el porcentaje está entre 0% y 10%. Si devuelve `False` para un coordinador, la cotización transiciona a `Pendiente de autorización`.
2. **`CotizacionDentroDeLimiteCoordinadorSpec` (RN-02):** Evalúa si la superficie es menor o igual a 300 m2 y el monto es menor o igual a $8,000 MXN.
3. **`CancelacionSinPenalizacionSpec` (RN-04):** Evalúa si la diferencia entre la fecha programada y la fecha de solicitud de cancelación es de 24 horas o más.
4. **`ClienteSuperaLimiteReprogramacionesSpec` (RN-08):** Evalúa si el conteo mensual de reprogramaciones del cliente es mayor a 2 para disparar la alerta a gerencia.
5. **`CuadrillaDisponibleSpec` (CA-06.3, CA-07.2):** Evalúa que el intervalo `[inicio_nuevo, fin_nuevo]` no se traslape con ninguna ventana `[inicio_existente, fin_existente]` de la cuadrilla.

### 3.2 Patrón State Machine (`src/domain/state_machines.py`)
Se implementaron dos máquinas de estados deterministas que gobiernan las transiciones permitidas:

1. **`CotizacionStateMachine` (`EstadoCotizacion`):**
   * Estados: `Borrador`, `Pendiente de autorización`, `Autorizada`, `Propuesta descartada`, `Enviada`, `Aceptada`, `Rechazada`.
   * Reglas de transición: Permite pasar de `Borrador` directamente a `Aceptada` cuando la cotización cumple los límites automáticos del coordinador (RN-01 y RN-02), pero si excede el 10% de descuento o los 300 m2 / $8,000, fuerza la transición a `Pendiente de autorización`, desde donde está prohibido pasar a `Aceptada` sin antes ser `Autorizada` por Gerencia (US-04). Una vez en `Aceptada`, no existen transiciones salientes permitidas, garantizando su inmutabilidad (CA-05.4).
2. **`OrdenServicioStateMachine` (`EstadoOrdenServicio`):**
   * Estados: `Generada`, `Programada`, `En ejecución`, `Pendiente de conformidad`, `Cerrado con conformidad`, `Cerrado con inconformidad`, `Cancelado sin cargo`, `Cancelado con cargo`, `No ejecutado con cargo`, `Facturada`.
   * Reglas de transición: Impide pasar de `Generada` a `En ejecución` sin antes haber pasado por `Programada` (asignación de fecha y cuadrilla), e impide pasar a cualquier estado de cierre sin haber estado en `En ejecución` (CA-09.2). Sólo los estados con obligación de pago pueden transicionar al estado `Facturada` (US-18).

### 3.3 Service Layer y Separación de Vistas (`src/application/services.py` y `src/api/`)
* **Service Layer:** Dividido en cuatro servicios cohesivos (`ServicioCotizacion`, `ServicioProgramacion`, `ServicioEjecucion`, `ServicioExcepciones`) que orquestan los casos de uso sobre `CleanProRepository`.
* **Capa de Presentación Desacoplada (`src/api/`):**
  * `GET /` (`index.html`): Portal Público del Cliente.
  * `GET /admin` (`admin.html`): Intranet Operativa y Administrativa.
  * `GET /docs`: Interfaz interactiva OpenAPI / Swagger UI.

---

## 4. Aplicación Demostrable de Principios SOLID

1. **S - Single Responsibility Principle (Responsabilidad Única):**
   * Cada clase y vista tiene una única razón para cambiar: `CotizacionStateMachine` sólo valida transiciones de cotización; `DescuentoAutorizablePorCoordinadorSpec` sólo evalúa RN-01; `index.html` atiende exclusivamente la experiencia del cliente y `admin.html` atiende la gestión interna.
2. **O - Open/Closed Principle (Abierto/Cerrado):**
   * Las políticas de negocio están abiertas a la extensión y cerradas a la modificación mediante la clase abstracta `Specification[T]`. Se pueden agregar nuevas reglas creando nuevas subclases sin alterar las existentes.
3. **L - Liskov Substitution Principle (Sustitución de Liskov):**
   * Cualquier subclase de `Specification[T]` puede sustituir a la clase base retornando consistentemente un booleano sin efectos secundarios sobre las entidades evaluadas.
4. **I - Interface Segregation Principle (Segregación de Interfaces):**
   * Tanto la capa de servicios (`ServicioCotizacion`, `ServicioProgramacion`, `ServicioEjecucion`, `ServicioExcepciones`) como la capa de presentación (`/` para clientes vs. `/admin` para personal interno) están segregadas por rol para que ningún actor dependa de operaciones que no le corresponden.
5. **D - Dependency Inversion Principle (Inversión de Dependencias):**
   * El núcleo del dominio (`src/domain/`) no depende de FastAPI, HTML ni bases de datos externas. Los servicios de aplicación reciben el repositorio por inyección de dependencias.