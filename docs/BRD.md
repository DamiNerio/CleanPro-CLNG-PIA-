# Business Requirements Document (BRD) - Caso 12: CleanPro

**Universidad Autónoma de Nuevo León**  
**Facultad de Ingeniería Mecánica y Eléctrica (FIME)**  
**Unidad de Aprendizaje:** Componentes de Lógica de Negocios (CLNG)  
**Docente:** Ing. Miguel Ángel Gómez Marroquín  
**Equipo:** 12 | **Grupo:** 004 | **Hora:** Martes M4-M6  

| Nombre del Integrante | Matrícula | Carrera |
| :--- | :--- | :--- |
| Camila Trujillo Quintanilla | 2162775 | ITS |
| Cesar Damian Nerio Gonzalez | 2161751 | ITS |
| Jesús Enrique López Martínez | 2162022 | ITS |

---

## 1. Levantamiento de Requerimientos (Entrevista con Stakeholder)

1. **¿Qué evento marca el inicio formal del proceso de cotización? ¿Puede un cliente solicitar cotización sin haber sido cliente antes?**  
   *Respuesta:* El proceso inicia cuando el cliente llama, escribe por WhatsApp o llena el formulario de la página para pedir cotización. No es necesario haber sido cliente antes; los prospectos nuevos entran al mismo flujo.
2. **¿Qué evento marca el cierre completo del proceso: la ejecución del servicio, el pago, o la conformidad del cliente?**  
   *Respuesta:* Formalmente cerramos el caso cuando el supervisor registra que el servicio terminó y el cliente firma de conformidad. La facturación es un proceso aparte que a veces se atrasa respecto a esto, y ahí hemos tenido problemas.
3. **¿Quién tiene autoridad para aprobar descuentos o ajustes de precio en la cotización?**  
   *Respuesta:* Solo yo (Gerencia) o el dueño autorizamos descuentos mayores al 10%. Los coordinadores pueden dar hasta 10% por su cuenta, sobre todo en contratos de frecuencia.
4. **¿El coordinador puede modificar una cotización ya enviada al cliente? ¿Bajo qué condiciones?**  
   *Respuesta:* Sí, mientras el cliente no la haya aceptado. Una vez aceptada, cualquier cambio requiere una nueva cotización o un ajuste que hoy manejamos de forma informal, por correo.
5. **¿Quién puede cancelar un servicio ya programado, y con cuánto tiempo de anticipación se permite sin penalización?**  
   *Respuesta:* El cliente puede cancelar sin costo hasta 24 horas antes. Con menos de 24 horas se cobra el 50%, salvo causas de fuerza mayor que evalúa el coordinador.
6. **¿Existe un tiempo máximo para responder una solicitud de cotización?**  
   *Respuesta:* Buscamos responder en menos de 4 horas hábiles, pero no es una regla formal ni se mide actualmente.
7. **¿Hay un monto o superficie límite que un coordinador puede autorizar sin pedir aprobación adicional?**  
   *Respuesta:* Puede cotizar y confirmar servicios de hasta 300 m2 o $8,000 MXN sin pedirme aprobación. Arriba de eso, me consultan.
8. **¿Cuántas reprogramaciones de un mismo servicio se consideran "normales" antes de tratarse como caso especial?**  
   *Respuesta:* No hay un límite definido; lo manejamos "a ojo". Si un cliente reprograma más de dos veces en un mes, el coordinador me avisa, pero no queda registrado en ningún lado.
9. **Cuando falta un integrante de la cuadrilla el día del servicio, ¿qué protocolo sigue el supervisor?**  
   *Respuesta:* El supervisor intenta reasignar a alguien de otra cuadrilla cercana. Si no encuentra reemplazo, se reduce el equipo y se avisa al cliente que el servicio podría tardar más. Reprogramar es la última opción.
10. **Si el cliente no permite el acceso al inmueble, ¿se cobra alguna penalización? ¿Quién lo decide?**  
    *Respuesta:* Se cobra el 100%, porque ya movilizamos personal. Lo decide el supervisor en el momento y administración lo valida al facturar.
11. **Cuando se pide un servicio adicional en sitio, ¿la cuadrilla puede realizarlo de inmediato o requiere autorización?**  
    *Respuesta:* La cuadrilla no puede aceptarlo por su cuenta. Deben llamar al coordinador, quien cotiza el extra y confirma con el cliente antes de hacerlo.
12. **Si el inmueble resulta más grande de lo reportado, ¿cómo se ajusta el precio y quién lo autoriza?**  
    *Respuesta:* El supervisor toma fotos y reporta al coordinador, quien recalcula el precio proporcional. Si el cliente no acepta el ajuste, se hace solo lo originalmente cotizado.
13. **¿Qué datos exactos captura el coordinador al generar la cotización?**  
    *Respuesta:* Ubicación, tipo de inmueble, superficie en m2, número de habitaciones/áreas, frecuencia, extras solicitados y datos de contacto del cliente.
14. **¿Qué información registra el supervisor al iniciar y terminar el servicio?**  
    *Respuesta:* Hora de inicio y término, cuadrilla asignada, incidencias si las hay, y firma del cliente en una hoja de servicio física. No siempre se toman fotos, y eso ha sido un problema.
15. **¿Cómo se documentan hoy las incidencias, y por qué hay "poca evidencia" según lo reportado?**  
    *Respuesta:* Se anotan en la hoja de papel, que después se captura en Excel si acaso. Muchas veces la hoja se pierde o se llena incompleta.
16. **¿Cómo llegan actualmente los cambios de personal a administración? ¿Por qué se pierden?**  
    *Respuesta:* El supervisor avisa al coordinador por WhatsApp, y el coordinador debería avisar a administración para nómina, pero muchas veces se le olvida o el mensaje se pierde entre tantos chats.
17. **¿Qué reportes o indicadores usa hoy la gerencia para medir el negocio?**  
    *Respuesta:* Solo llevamos un Excel de cotizaciones cerradas por mes e ingresos totales. No medimos tiempos de respuesta, incidencias ni satisfacción del cliente de forma sistemática.
18. **¿Cuáles son las 2-3 prioridades a resolver primero y cómo medirán que el proyecto tuvo éxito?**  
    *Respuesta:* Lo más urgente es resolver la facturación para que no se nos escapen servicios sin cobrar y que los cambios de personal lleguen a administración sin depender de que alguien se acuerde de avisar. Sabremos que funcionó si bajan los errores de facturación y las quejas por incidencias no atendidas.

---

## 2. Definición Estratégica del Negocio

### 2.1 Contexto
CleanPro presta servicios de limpieza residencial y empresarial. El precio depende de las características del inmueble, la frecuencia del servicio y los extras solicitados. El proceso central abarca cotización, programación, asignación de cuadrillas y ejecución del servicio, con participación de cliente, coordinador, cuadrilla, supervisor, administración y gerencia.

### 2.2 Problema / Oportunidad
* **Pérdida de información para nómina:** Los cambios de personal (ausencias, sustituciones) se comunican de manera informal (WhatsApp) y frecuentemente no llegan a administración, generando errores de nómina.
* **Fugas de facturación:** No existe un vínculo confiable entre el servicio ejecutado y su cobro, provocando que se escapen servicios ejecutados sin facturar.
* **Operación manual:** Las asignaciones de cuadrillas son manuales, sin reglas de validación de traslapes ni disponibilidad centralizada.
* **Evidencia deficiente:** Hay poca evidencia de incidencias y de servicios adicionales realizados en sitio (las hojas de papel se pierden o se llenan incompletas).
* **Políticas informales:** No existen controles automatizados para límites de descuentos, cancelaciones y reprogramaciones; se manejan "a ojo" según la experiencia del coordinador.
* **Falta de indicadores:** No hay reportes sistemáticos más allá de un archivo Excel básico de cotizaciones e ingresos.

**Oportunidad:** Digitalizar el ciclo completo de cotización-programación-asignación-ejecución-facturación mediante un sistema web y API REST basado en lógica de negocio (DDD, Specification y State Machine) que separe la vista comercial del cliente (`/`) de la intranet operativa y administrativa (`/admin`), garantizando trazabilidad de extremo a extremo.

### 2.3 Stakeholders

| Rol | Participación Principal | Vista del Sistema Asignada |
| :--- | :--- | :--- |
| **Cliente / Prospecto** | Solicita cotización en línea, acepta propuestas, cancela citas y firma digitalmente de conformidad o inconformidad al finalizar. | Portal Público del Cliente (`/`) |
| **Coordinador** | Cotiza, programa fechas, asigna cuadrillas disponibles, autoriza descuentos de hasta 10%, gestiona reprogramaciones y cotiza extras en sitio. | Intranet Operativa (`/admin`) |
| **Cuadrilla** | Ejecuta el servicio de limpieza conforme al alcance autorizado y reporta ausencias, extras solicitados o incidencias al supervisor. | Intranet Operativa (`/admin`) |
| **Supervisor** | Valida acceso al inmueble, registra marca de inicio y término, documenta incidencias con evidencia fotográfica y reporta cambios de personal. | Intranet Operativa (`/admin`) |
| **Administración** | Valida cargos por penalización, emite facturas vinculadas a órdenes cerradas y procesa los cambios de personal para nómina. | Intranet Administrativa (`/admin`) |
| **Gerencia (Lic. Renata Cárdenas)** | Autoriza descuentos mayores al 10% y servicios que superen 300 m2 u $8,000 MXN, monitorea alertas de reprogramación y consulta KPIs. | Intranet Administrativa (`/admin`) |

### 2.4 Alcance del Proyecto
* **Dentro del alcance:** Portal web público para clientes (`/`), intranet administrativa para personal interno (`/admin`), API REST documentada con OpenAPI/Swagger (`/docs`), cálculo automático de cotización, autorización por niveles de rol, programación y asignación de cuadrillas sin traslapes, ejecución y cierre con acta digital, manejo de excepciones (ausencia de personal, acceso denegado, extras en sitio, inmueble mayor a lo reportado, cancelaciones y reprogramaciones), registro de incidencias con evidencia, generación de registros facturables y avisos directos a nómina.
* **Fuera del alcance:** Timbrado fiscal PAC ante el SAT, dispersión bancaria de nómina, pasarela de cobro con tarjeta de crédito y aplicación móvil nativa iOS/Android.

### 2.5 Necesidades del Negocio
* **N-01:** Reglas claras, automatizadas y parametrizables para descuentos, límites de cotización, cancelaciones y reprogramaciones.
* **N-02:** Canal estructurado para que los cambios de personal lleguen el mismo día a administración sin depender de WhatsApp.
* **N-03:** Vinculación obligatoria entre cada servicio cerrado (o penalizado) y su registro facturable correspondiente.
* **N-04:** Captura obligatoria de evidencia digital (fotografías, notas y firmas) en incidencias, ajustes de superficie y cierres de servicio.
* **N-05:** Límites jerárquicos de autorización claramente diferenciados entre Coordinador y Gerencia, aislando la operación interna de la vista del cliente.
* **N-06:** Reportes e indicadores automáticos de cotizaciones, órdenes, cambios de nómina y facturación pendiente.

### 2.6 Restricciones y Supuestos
* **Restricciones:** Los umbrales numéricos (10%, 300 m2, $8,000, 24 horas, 4 horas) se gestionan como variables de entorno configurables sujetas a confirmación con el stakeholder.
* **Supuestos:** CleanPro opera en una sola región metropolitana; cada cuadrilla atiende un único servicio a la vez; la firma digital del cliente capturada en el portal web tiene plena validez como evidencia de cierre.

### 2.7 Criterios de Éxito Medibles
* **0%** de servicios ejecutados o penalizados sin registro facturable vinculado.
* **100%** de los cambios de personal registrados por supervisores y visibles en el tablero de administración el mismo día.
* **Al menos 95%** de las incidencias y servicios adicionales documentados con evidencia digital.
* **Menos de 4 horas hábiles** de tiempo de respuesta en cotizaciones medido de forma sistemática.

---

## 3. Reglas de Negocio de Referencia (RN)

| Clave | Regla de Negocio | Origen |
| :--- | :--- | :--- |
| **RN-01** | Descuentos de hasta 10% los autoriza el coordinador; los mayores al 10% requieren autorización de gerencia o del dueño. | Pregunta 3 |
| **RN-02** | El coordinador puede cotizar y confirmar servicios de hasta 300 m2 u $8,000 MXN sin aprobación adicional. Arriba de esos límites requiere autorización de gerencia. | Pregunta 7 |
| **RN-03** | La respuesta a una solicitud de cotización debe emitirse en un máximo de 4 horas hábiles (SLA). | Pregunta 6 |
| **RN-04** | Cancelación sin costo con 24 horas o más de anticipación; con menos de 24 horas se cobra una penalización del 50%, salvo fuerza mayor evaluada por el coordinador. | Pregunta 5 |
| **RN-05** | Si el cliente no permite el acceso al inmueble en la fecha programada, se cobra una penalización del 100%; lo registra el supervisor con evidencia y administración lo valida al facturar. | Pregunta 10 |
| **RN-06** | Los servicios adicionales solicitados en sitio requieren cotización del coordinador y autorización explícita del cliente antes de ejecutarse; la cuadrilla no puede aceptarlos por su cuenta. | Pregunta 11 |
| **RN-07** | Si el inmueble resulta mayor a lo reportado, el coordinador recalcula el precio de forma proporcional con evidencia fotográfica; si el cliente no acepta, se ejecuta únicamente lo cotizado. | Pregunta 12 |
| **RN-08** | Más de 2 reprogramaciones del mismo cliente en un periodo de 30 días se tratan como caso especial y generan una alerta automática a gerencia. | Pregunta 8 |
| **RN-09** | Toda cotización aceptada genera automáticamente una Orden de Servicio, y todo servicio cerrado (o con penalización) genera un Registro Facturable vinculado. | Preguntas 2 y 18 |

---

## 4. Historias de Usuario y Criterios de Aceptación (Gherkin)

### Módulo 1: Cotización

#### US-01 - Solicitud de cotización en línea (Cliente)
> **Como** cliente, **quiero** solicitar una cotización en línea indicando ubicación, tipo de inmueble, superficie, frecuencia y extras, **para** no depender de llamar por teléfono.

* **CA-01.1:** El formulario del Portal del Cliente (`/`) captura ubicación, tipo de inmueble, superficie en m2, frecuencia, extras solicitados y datos de contacto.
* **CA-01.2:** El sistema impide enviar la solicitud si falta algún campo obligatorio e indica cuál es, sin borrar la información ya capturada.
* **CA-01.3:** La superficie sólo acepta valores numéricos mayores a cero (> 0).
* **CA-01.4:** Al enviarse, la solicitud recibe un folio único y queda registrada con fecha, hora y canal de origen (`web`, `WhatsApp` o `llamada`).
* **CA-01.5:** No se exige historial previo: un prospecto nuevo puede completar el flujo sin registro de cliente existente.

```gherkin
Característica: Solicitud de cotización en línea

  Escenario: Prospecto nuevo envía una solicitud completa
    Dado que soy un prospecto sin historial en CleanPro
    Y me encuentro en el formulario web del Portal del Cliente
    Cuando capturo ubicación, tipo de inmueble "casa", superficie de 120 m2, frecuencia quincenal, el extra "limpieza de vidrios" y mis datos de contacto
    Y envío la solicitud
    Entonces el sistema registra la solicitud con un folio único, fecha, hora y canal "web"
    Y muestra un acuse con el folio al prospecto
    Y la solicitud aparece en la bandeja del coordinador en la Intranet

  Escenario: Solicitud incompleta o con superficie inválida
    Dado que estoy capturando una solicitud de cotización
    Cuando dejo vacío el campo de ubicación o ingreso una superficie menor o igual a 0
    Entonces el sistema no registra la solicitud
    Y señala el dato obligatorio faltante o inválido
```

#### US-02 - Sugerencia de duración y personal estimado (Coordinador)
> **Como** coordinador, **quiero** que el sistema me sugiera duración y personal estimado según el tamaño del inmueble y los extras, **para** agilizar la cotización.

* **CA-02.1:** Al crearse la solicitud, el sistema propone duración estimada en horas y número de personas a partir de la superficie y los extras.
* **CA-02.2:** Los parámetros de cálculo (rendimiento en m2 por persona-hora y tiempo por extra) son configurables mediante variables de entorno sin cambios de código.
* **CA-02.3:** El coordinador puede consultar y ajustar la cotización desde la Intranet (`/admin`).
* **CA-02.4:** Si falta algún dato necesario para el cálculo, se indica cuál es en lugar de mostrar una estimación en cero.

```gherkin
Característica: Sugerencia automática de recursos de limpieza

  Escenario: Sugerencia automática a partir del tamaño del inmueble
    Dado que el parámetro de rendimiento está configurado en 60 m2 por persona-hora
    Y el extra "limpieza de vidrios" suma 1 hora
    Cuando se genera la cotización de un inmueble de 240 m2 con ese extra
    Entonces el sistema sugiere 5 horas-persona de trabajo
    Y propone una cuadrilla de 2 personas
```

#### US-03 - Descuento de hasta 10% aplicado por el coordinador (Coordinador)
> **Como** coordinador, **quiero** aplicar descuentos de hasta 10% directamente en la cotización, **para** atender contratos de frecuencia sin escalar cada caso a gerencia.

* **CA-03.1:** El campo de descuento acepta valores de 0% a 10% cuando el usuario tiene rol de coordinador (RN-01).
* **CA-03.2:** Un descuento mayor al 10% no puede aprobarse directamente por el coordinador: el sistema lo bloquea, cambia el estado a `Pendiente de autorización` y requiere aprobación de gerencia.
* **CA-03.3:** Todo descuento aplicado registra porcentaje, motivo, usuario y fecha.
* **CA-03.4:** El total de la cotización se recalcula automáticamente al aplicar el descuento.

```gherkin
Característica: Aplicación de descuentos por el coordinador

  Escenario: Descuento dentro del límite del coordinador
    Dado que tengo rol de coordinador en la Intranet Administrativa
    Y estoy elaborando una cotización de $10,000 para un contrato de frecuencia semanal
    Cuando aplico un descuento de 8% con el motivo "contrato de frecuencia"
    Entonces el sistema acepta el descuento sin autorización adicional
    Y el total de la cotización queda en $9,200

  Escenario: Descuento fuera del límite del coordinador
    Dado que tengo rol de coordinador
    Cuando intento aplicar un descuento de 15%
    Entonces el sistema no aprueba directamente el descuento
    Y cambia la cotización a estado "Pendiente de autorización"
    Y la envía a la bandeja de Gerencia
```

#### US-04 - Alerta y autorización de descuentos mayores al 10% o límites excedidos (Gerencia)
> **Como** gerente, **quiero** recibir una alerta cuando una cotización requiera un descuento mayor al 10% o supere 300 m2 / $8,000, **para** autorizarla antes de que el cliente la acepte.

* **CA-04.1:** Al solicitarse un descuento mayor al 10% (RN-01) o excederse 300 m2 / $8,000 (RN-02), la cotización aparece en la bandeja de autorizaciones de Gerencia en `/admin`.
* **CA-04.2:** Mientras la solicitud está en `Pendiente de autorización`, el Portal del Cliente (`/`) muestra el estado *En revisión comercial* y deshabilita el botón de aceptación.
* **CA-04.3:** La Gerencia puede autorizar la excepción con un clic en `/admin`.
* **CA-04.4:** La resolución registra el usuario de gerencia (`Lic. Renata Cárdenas`).
* **CA-04.5:** Al autorizarse, la cotización cambia a estado `Autorizada` y habilita la aceptación para el cliente.

```gherkin
Característica: Autorización gerencial de cotizaciones excepcionales

  Escenario: Gerencia autoriza el descuento solicitado
    Dado que el coordinador solicitó un descuento de 15% en la cotización COT-1042
    Y la cotización está en estado "Pendiente de autorización"
    Cuando la gerente autoriza la solicitud desde la Intranet
    Entonces la cotización cambia a estado "Autorizada"
    Y el Portal del Cliente habilita el botón para aceptar la propuesta

  Escenario: Intento de aceptación o envío sin autorización
    Dado que la cotización COT-1042 está en estado "Pendiente de autorización"
    Cuando se intenta enviar o aceptar sin visto bueno de gerencia
    Entonces el sistema bloquea la operación
    Y muestra que requiere autorización de gerencia
```

#### US-05 - Aceptación o rechazo de la cotización por el cliente (Cliente)
> **Como** cliente, **quiero** aceptar o rechazar la cotización desde el Portal del Cliente, **para** agilizar mi decisión.

* **CA-05.1:** El cliente puede aceptar su cotización directamente desde el Portal Público (`/`).
* **CA-05.2:** Una cotización dentro de los límites del coordinador (`Borrador` o `Enviada`) o ya `Autorizada` por gerencia puede pasar directamente a `Aceptada`.
* **CA-05.3:** Una cotización aceptada genera automáticamente la Orden de Servicio asociada en estado `Generada` (RN-09).
* **CA-05.4:** Una cotización en estado `Aceptada` es inmutable: cualquier intento posterior de editar su descuento es bloqueado por el dominio.

```gherkin
Característica: Resolución de la cotización por el cliente

  Escenario: El cliente acepta la cotización en su portal
    Dado que visualizo mi cotización COT-1042 en el Portal del Cliente
    Cuando hago clic en el botón "Aceptar Propuesta"
    Entonces el sistema cambia la cotización a estado "Aceptada"
    Y genera automáticamente la orden de servicio SRV-1042

  Escenario: Cotización aceptada no editable
    Dado que la cotización COT-1042 está en estado "Aceptada"
    Cuando el coordinador intenta modificar el descuento
    Entonces el sistema impide la edición
```

---

### Módulo 2: Programación y Asignación

#### US-06 - Programación de fecha y hora del servicio (Coordinador)
> **Como** coordinador, **quiero** programar fecha y hora del servicio una vez aceptada la cotización, **para** que quede agendado en el calendario del negocio.

* **CA-06.1:** Sólo pueden programarse órdenes provenientes de cotizaciones aceptadas.
* **CA-06.2:** La programación exige fecha, hora de inicio y cuadrilla operativa desde la Intranet (`/admin`).
* **CA-06.3:** El sistema bloquea la programación en un horario que ya está ocupado por la misma cuadrilla.
* **CA-06.4:** El servicio programado cambia a estado `Programada` y es visible para el supervisor en `/admin` y como *Equipo asignado* para el cliente en `/`.

```gherkin
Característica: Programación de órdenes de servicio

  Escenario: Programación válida de un servicio aceptado
    Dado que la cotización COT-1042 está aceptada y generó la orden SRV-1042
    Y la cuadrilla C-05 no tiene otro servicio el 20 de noviembre a las 09:00
    Cuando el coordinador programa el servicio el 20 de noviembre a las 09:00 con C-05
    Entonces el servicio cambia a estado "Programada"

  Escenario: Traslape de horarios
    Dado que la cuadrilla C-03 ya tiene un servicio el 20 de noviembre de 08:00 a 13:00
    Cuando intento programarle otro servicio el mismo día a las 10:00
    Entonces el sistema rechaza la programación con error 409 Conflict
    Y muestra que existe un traslape de horario
```

#### US-07 - Asignación de cuadrilla disponible (Coordinador)
> **Como** coordinador, **quiero** asignar una cuadrilla disponible a cada servicio programado, **para** evitar choques de horario o de personal.

* **CA-07.1:** El sistema valida mediante `CuadrillaDisponibleSpec` la disponibilidad en la ventana de fecha y hora del servicio.
* **CA-07.2:** Una cuadrilla no puede quedar asignada a dos servicios traslapados.
* **CA-07.3:** La asignación registra la cuadrilla y sus integrantes en la orden de servicio.

```gherkin
Característica: Asignación de cuadrilla disponible

  Escenario: Asignación exitosa de cuadrilla sin traslape
    Dado que el servicio SRV-2210 requiere programación de 09:00 a 14:00
    Y la cuadrilla C-05 está libre en esa ventana
    Cuando asigno la cuadrilla C-05 al servicio SRV-2210
    Entonces la orden muestra la cuadrilla C-05 y sus integrantes
    Y la cuadrilla C-05 queda reservada en ese horario
```

#### US-08 - Consulta de la agenda del día por el supervisor (Supervisor)
> **Como** supervisor, **quiero** ver en la Intranet la cuadrilla y el detalle del servicio asignado para el día, **para** saber a dónde presentarme y qué se cotizó.

* **CA-08.1:** El supervisor consulta en la pestaña **2. Supervisor en Sitio** (`/admin`) las órdenes activas.
* **CA-08.2:** Cada orden muestra folio, cliente, superficie en m2, estado actual, cuadrilla asignada y conteo de incidencias.
* **CA-08.3:** La vista ofrece botones de acción directa para **Registrar Inicio** o reportar **Acceso Denegado (100%)**.

```gherkin
Característica: Consulta de agenda operativa del supervisor

  Escenario: Visualización de orden programada en la Intranet
    Dado que el coordinador asignó la cuadrilla C-07 al servicio SRV-2210
    Cuando el supervisor abre la pestaña de Supervisor en Sitio en /admin
    Entonces visualiza el servicio SRV-2210 con la cuadrilla C-07 lista para iniciar
```

---

### Módulo 3: Ejecución y Cierre

#### US-09 - Registro de hora de inicio y término del servicio (Supervisor)
> **Como** supervisor, **quiero** registrar la hora de inicio y término del servicio, **para** tener evidencia formal del tiempo real trabajado.

* **CA-09.1:** El registro de inicio toma la marca de tiempo oficial del servidor y transiciona la orden de `Programada` a `En ejecución`.
* **CA-09.2:** La máquina de estados (`OrdenServicioStateMachine`) impide pasar una orden a `En ejecución` si sigue en `Generada` (sin programar) e impide cerrarla si antes no se registró su inicio.

```gherkin
Característica: Control de tiempos de ejecución en sitio

  Escenario: Registro completo de la jornada
    Dado que el servicio SRV-2210 está en estado "Programada"
    Cuando el supervisor registra el inicio del servicio
    Entonces el sistema guarda la hora oficial del sistema y cambia el estado a "En ejecución"

  Escenario: Intento de término sin inicio registrado
    Dado que el servicio SRV-2210 está en estado "Programada" sin hora de inicio
    Cuando se intenta registrar el cierre del servicio
    Entonces el sistema bloquea la operación e indica que primero debe registrarse el inicio
```

#### US-10 - Registro de incidencias con evidencia digital (Supervisor)
> **Como** supervisor, **quiero** capturar fotos y notas de las incidencias ocurridas desde la Intranet, **para** dejar evidencia digital en lugar de hojas de papel que se pierden.

* **CA-10.1:** Una incidencia se registra con tipo, descripción y al menos una fotografía de evidencia.
* **CA-10.2:** Cada evidencia queda ligada a la orden de servicio.
* **CA-10.3:** El servicio no puede cerrarse si contiene incidencias registradas sin descripción o sin evidencia fotográfica (CA-10.4).

```gherkin
Característica: Documentación digital de incidencias en sitio

  Escenario: Incidencia documentada con fotografía
    Dado que durante el servicio SRV-2210 se daña una persiana
    Cuando el supervisor registra la incidencia de tipo "daño en mobiliario" con descripción y foto en /admin
    Entonces la incidencia queda ligada al servicio SRV-2210

  Escenario: Intento de cierre con incidencia incompleta
    Dado que el servicio SRV-2210 tiene una incidencia registrada sin descripción
    Cuando se intenta cerrar el servicio
    Entonces el sistema bloquea el cierre y señala que la incidencia debe tener descripción
```

#### US-11 - Firma digital de conformidad del cliente (Cliente)
> **Como** cliente, **quiero** firmar digitalmente de conformidad desde mi portal al finalizar el servicio, **para** confirmar mi satisfacción o reportar inconformidad de inmediato.

* **CA-11.1:** Cuando la orden está `En ejecución`, el Portal del Cliente (`/`) habilita los botones **Firmar de Conformidad** y **Reportar Inconformidad**.
* **CA-11.2:** La firma digital almacena el nombre de quien firma, fecha, hora y el indicador de conformidad.
* **CA-11.3:** Si el cliente reporta inconformidad, el sistema exige un motivo obligatorio y cambia el estado a `Cerrado con inconformidad`.
* **CA-11.4:** Si el cliente firma de conformidad, la orden pasa a estado `Cerrado con conformidad`.

```gherkin
Característica: Firma digital de cierre de servicio

  Escenario: Cierre con firma de conformidad desde el Portal del Cliente
    Dado que el servicio SRV-2210 está en ejecución y tiene sus incidencias completas
    Cuando el cliente hace clic en "Firmar de Conformidad" e ingresa su nombre
    Entonces el servicio cambia a estado "Cerrado con conformidad"
    Y se genera automáticamente el registro facturable en Administración

  Escenario: Cliente inconforme
    Dado que el cliente no está satisfecho con el resultado del servicio SRV-2210
    Cuando selecciona "Reportar Inconformidad" con el motivo "faltó detallar ventanas"
    Entonces el servicio cambia a estado "Cerrado con inconformidad"
```

---

### Módulo 4: Excepciones Operativas

#### US-12 - Reporte de ausencia de un integrante de la cuadrilla (Supervisor)
> **Como** supervisor, **quiero** reportar la ausencia de un integrante de la cuadrilla el día del servicio, **para** que quede actualizado el equipo y se notifique a nómina.

* **CA-12.1:** Desde la pestaña **2. Supervisor en Sitio** en `/admin`, el supervisor reporta la ausencia indicando orden, integrante ausente, reemplazo opcional y motivo.
* **CA-12.2:** Si hay reemplazo, se actualiza la lista de integrantes de la cuadrilla; si no, se registra como `Equipo reducido`.
* **CA-12.3:** El reporte alimenta de inmediato el tablero de cambios de personal de Administración para nómina (US-17).

```gherkin
Característica: Gestión de ausencias de personal en cuadrilla

  Escenario: Se reporta ausencia y se asigna un reemplazo
    Dado que el integrante "J. Ramírez" no se presentó al servicio SRV-2210
    Cuando el supervisor reporta la ausencia indicando el reemplazo "C. Nuevo" en /admin
    Entonces la cuadrilla actualiza sus integrantes
    Y se crea el registro estructurado en la bandeja de Nómina de Administración
```

#### US-13 - Registro de acceso denegado al inmueble (Supervisor / Coordinador)
> **Como** supervisor, **quiero** registrar cuando un cliente no permite el acceso al inmueble, **para** aplicar la penalización del 100% de forma consistente.

* **CA-13.1:** El supervisor presiona el botón **Acceso Denegado (100%)** en `/admin` adjuntando la evidencia correspondiente.
* **CA-13.2:** El sistema aplica automáticamente el cargo del 100% del servicio conforme a la regla RN-05.
* **CA-13.3:** El servicio transiciona al estado `No ejecutado con cargo`, libera el horario de la cuadrilla y genera el registro facturable al 100%.

```gherkin
Característica: Penalización por acceso denegado al inmueble

  Escenario: Acceso denegado con evidencia fotográfica
    Dado que la cuadrilla llegó al domicilio del servicio programado SRV-2215
    Y nadie permite el acceso al inmueble
    Cuando el supervisor registra "acceso denegado" con evidencia
    Entonces el servicio cambia a estado "No ejecutado con cargo"
    Y el sistema genera un registro facturable por el 100% del monto cotizado
```

#### US-14 - Autorización de servicios adicionales solicitados en sitio (Cuadrilla / Coordinador)
> **Como** cuadrilla, **quiero** solicitar autorización al coordinador cuando el cliente pide un servicio adicional en sitio, **para** no realizar trabajo no cotizado sin aprobación.

* **CA-14.1:** Ningún servicio extra se suma al total sin autorización explícita del cliente (RN-06).
* **CA-14.2:** Si el cliente autoriza el extra, la orden incorpora el trabajo y suma su costo al precio total; si lo rechaza, mantiene el alcance original.

```gherkin
Característica: Autorización de servicios adicionales en sitio

  Escenario: Extra autorizado por el cliente
    Dado que el cliente solicita en sitio la limpieza de una terraza no cotizada
    Cuando el coordinador cotiza el extra en $900 y el cliente lo autoriza
    Entonces la orden de servicio incorpora el extra y suma $900 al precio total
```

#### US-15 - Recálculo de precio cuando el inmueble es mayor a lo reportado (Coordinador)
> **Como** coordinador, **quiero** recalcular el precio cuando el inmueble resulta más grande de lo reportado, **para** cobrar de forma justa y transparente.

* **CA-15.1:** El ajuste exige evidencia fotográfica obligatoria y una superficie real medida en sitio mayor a la cotizada (RN-07).
* **CA-15.2:** Si el cliente autoriza el ajuste, el sistema recalcula el precio total de forma proporcional (`nueva_superficie / superficie_original`).

```gherkin
Característica: Ajuste proporcional por superficie mayor en sitio

  Escenario: El cliente acepta el ajuste proporcional
    Dado que el servicio SRV-2210 se cotizó originalmente para 150 m2
    Y el supervisor mide 200 m2 reales en sitio y adjunta fotografías de evidencia
    Cuando el coordinador recalcula el precio de forma proporcional y el cliente acepta
    Entonces la orden de servicio actualiza su superficie a 200 m2
    Y el precio total aumenta proporcionalmente en un factor de 200/150
```

#### US-16 - Solicitud de reprogramación o cancelación por el cliente (Cliente)
> **Como** cliente, **quiero** solicitar una reprogramación o cancelación desde mi portal, **para** gestionar mi cita con transparencia sobre los cargos aplicables.

* **CA-16.1:** El sistema evalúa la anticipación respecto a la fecha y hora programada conforme a la regla RN-04.
* **CA-16.2:** Con 24 horas o más (o fuerza mayor), pasa a `Cancelado sin cargo` (0%). Con menos de 24 horas, pasa a `Cancelado con cargo` y genera un registro facturable por el 50%.
* **CA-16.3:** Al cancelar o reprogramar, se libera la ventana original de la cuadrilla y se contabilizan las reprogramaciones mensuales del cliente para alertar a gerencia si supera 2 en el mes (RN-08).

```gherkin
Característica: Políticas de cancelación y reprogramación

  Escenario: Cancelación tardía con menos de 24 horas
    Dado que el servicio SRV-2210 está programado para mañana a las 09:00
    Y faltan 12 horas para su inicio
    Cuando el cliente confirma la cancelación desde su portal
    Entonces el servicio cambia a estado "Cancelado con cargo"
    Y el sistema genera un registro facturable por el 50% del monto del servicio
```

---

### Módulo 5: Administración y Reportes

#### US-17 - Llegada automática de los cambios de personal a administración (Administración)
> **Como** administración, **quiero** recibir automáticamente en la Intranet los cambios de personal registrados por el supervisor, **para** actualizar la nómina sin depender de mensajes informales.

* **CA-17.1:** Toda ausencia o sustitución registrada por el supervisor genera un registro estructurado (`NOM-1`, `NOM-2`...) con folio de orden, integrante saliente, integrante entrante y motivo.
* **CA-17.2:** El registro aparece en tiempo real en la pestaña **3. Gerencia y Administración** de `/admin` e incrementa el KPI de cambios en nómina.

```gherkin
Característica: Sincronización de cambios de personal con nómina

  Escenario: Cambio de personal visible en el tablero administrativo
    Dado que el supervisor registró una sustitución de personal en el servicio SRV-2210
    Cuando administración consulta la pestaña de Gerencia y Administración en /admin
    Entonces visualiza el registro con el integrante saliente, entrante y motivo
```

#### US-18 - Vinculación entre servicio ejecutado y factura (Administración)
> **Como** administración, **quiero** que cada servicio finalizado o penalizado quede vinculado a su registro facturable, **para** evitar servicios ejecutados y no cobrados.

* **CA-18.1:** Todo servicio cerrado (`Cerrado con conformidad` o `Cerrado con inconformidad`) o penalizado (`Cancelado con cargo` del 50% o `No ejecutado con cargo` del 100%) genera automáticamente su Registro Facturable en la bandeja de Administración en `/admin` (RN-09).

```gherkin
Característica: Control de facturación vinculada a órdenes

  Escenario: Servicio cerrado genera registro facturable automático
    Dado que el servicio SRV-2210 se cerró con firma de conformidad del cliente
    Cuando administración consulta la bandeja de Registros Facturables en /admin
    Entonces el servicio SRV-2210 aparece listado con su importe total listo para facturar
```

#### US-19 - Reportes e indicadores para la gerencia (Gerencia)
> **Como** gerente, **quiero** consultar en tiempo real los indicadores de cotizaciones, órdenes, servicios pendientes de facturar y cambios de nómina, **para** tomar decisiones basadas en datos.

* **CA-19.1:** Los endpoints `/api/administracion/kpis` y `/api/estado` alimentan las tarjetas superiores de la Intranet (`/admin`) sin recaptura manual en Excel.

```gherkin
Característica: Tablero de indicadores clave de desempeño (KPIs)

  Escenario: Consulta de indicadores operativos y de facturación
    Dado que existen cotizaciones atendidas, servicios cerrados y cambios de personal
    Cuando la gerente abre la Intranet Administrativa (/admin) o consulta /api/administracion/kpis
    Entonces visualiza en tiempo real el total de cotizaciones, órdenes, pendientes de facturar y cambios de nómina
```

---

## 5. Glosario de Dominio (Lenguaje Ubicuo - 22 Términos)

| # | Término Ubicuo | Definición en el Dominio de CleanPro |
| :--- | :--- | :--- |
| 1 | **Prospecto** | Usuario que solicita una cotización inicial en el Portal del Cliente sin requerir historial previo. |
| 2 | **Cliente** | Persona física o moral que acepta una cotización formal y recibe servicios de limpieza. |
| 3 | **Solicitud de Cotización** | Petición de entrada por canal web, WhatsApp o teléfono que contiene datos del inmueble, frecuencia y extras. |
| 4 | **Cotización Formal** | Raíz de agregado de la fase comercial que encapsula el cálculo de costos, recursos sugeridos, descuentos y autorizaciones. |
| 5 | **Coordinador** | Rol operativo facultado en la Intranet para cotizar servicios de hasta 300 m2 y $8,000, aplicar descuentos de hasta 10%, programar fechas y asignar cuadrillas. |
| 6 | **Autorización de Gerencia** | Aprobación explícita de la Lic. Renata Cárdenas requerida cuando un descuento supera el 10% o el servicio excede 300 m2 u $8,000. |
| 7 | **Contrato de Frecuencia** | Modalidad de servicio periódico (semanal, quincenal, mensual) elegible para descuentos comerciales. |
| 8 | **Orden de Servicio** | Raíz de agregado de la fase operativa creada automáticamente al aceptarse una cotización; controla la ejecución, excepciones y cierre. |
| 9 | **Cuadrilla** | Equipo de operarios de limpieza con identidad única (`C-03`, `C-05`, `C-07`) que atiende un solo servicio a la vez sin traslape de horarios. |
| 10 | **Supervisor** | Responsable en sitio de validar el acceso al domicilio, registrar inicio, reportar ausencias y documentar incidencias desde `/admin`. |
| 11 | **Rendimiento Persona-Hora** | Parámetro técnico configurable (60 m2 por hora por defecto) utilizado para estimar las horas-hombre y el tamaño de cuadrilla requerido. |
| 12 | **Servicio Extra en Sitio** | Trabajo adicional no incluido en la cotización original que el cliente solicita durante la visita y que exige cotización del coordinador y autorización previa. |
| 13 | **Ajuste por Superficie Mayor** | Recálculo proporcional del precio de la orden cuando el metraje real medido en sitio con evidencia fotográfica supera lo reportado por el cliente. |
| 14 | **Incidencia** | Suceso imprevisto ocurrido durante la ejecución del servicio (ej. daño en mobiliario) que exige tipo, descripción y evidencia fotográfica. |
| 15 | **Acceso Denegado** | Excepción operativa en la que el cliente no permite la entrada al inmueble a la cuadrilla en el horario programado, generando un cargo del 100%. |
| 16 | **Cancelación Tardía** | Cancelación solicitada por el cliente con menos de 24 horas de anticipación respecto al inicio programado, sujeta a un cargo del 50%. |
| 17 | **Fuerza Mayor** | Causa extraordinaria validada por el coordinador que exime al cliente del cargo del 50% en una cancelación tardía. |
| 18 | **Reprogramación Recurrente** | Condición que se activa cuando un mismo cliente acumula más de 2 reprogramaciones en un mes, disparando una alerta a gerencia. |
| 19 | **Cambio de Personal** | Registro estructurado de ausencia o sustitución de un integrante de cuadrilla enviado directamente al tablero de administración para nómina. |
| 20 | **Acta Digital de Servicio** | Conjunto inmutable de datos de cierre de la orden compuesto por las marcas de tiempo reales, evidencias fotográficas y la firma digital del cliente. |
| 21 | **Firma de Conformidad** | Aprobación digital capturada por el cliente en su portal web al cierre del servicio; si se registra como inconformidad, exige capturar un motivo obligatorio. |
| 22 | **Registro Facturable** | Obligación de cobro generada automáticamente al cerrar un servicio o aplicar una penalización (50% o 100%) para garantizar cero fugas de facturación. |

---

## 6. Matriz de Trazabilidad Completa (Análisis <-> Arquitectura <-> Código y Vistas <-> Pruebas)

| Necesidad BRD | Regla | User Stories / Criterios | Actividad en BPMN | Componente DDD / Código y Vista (`src/`) | Pruebas Automatizadas (`tests/`) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **N-01, N-05:** Cotización ágil y límites por rol | RN-02, RN-03 | US-01, US-02, US-05 (CA-01 a CA-05) | Solicitud -> *Capturar datos y sugerir recursos* (`[DO1]`, `[DO2]`) | `CotizacionFormal`, `Superficie`, `CotizacionDentroDeLimiteCoordinadorSpec`, `ServicioCotizacion`, `index.html` (`/`) | `test_us01_y_us02_cotizacion_y_sugerencia_recursos`, `test_flujo_completo_cotizacion_descuento_y_autorizacion` |
| **N-01, N-05:** Control estricto de descuentos | RN-01 | US-03, US-04 (CA-03, CA-04) | Gateway `¿>10% desc. o >300m2/$8,000?` -> *Evaluar excepción* | `Descuento`, `DescuentoAutorizablePorCoordinadorSpec`, `CotizacionStateMachine`, `admin.html` (`/admin`) | `test_us03_y_us04_descuento_mayor_10_requiere_gerencia` |
| **N-01:** Programación sin traslapes de horario | RN-09 | US-06, US-07, US-08 (CA-06 a CA-08) | *Programar fecha y asignar cuadrilla* (`[DO3]`) -> *Consultar agenda* | `OrdenDeServicio`, `Cuadrilla`, `CuadrillaDisponibleSpec`, `ServicioProgramacion`, `admin.html` (`/admin`) | `test_us06_y_us07_bloqueo_traslape_cuadrilla` |
| **N-04:** Ejecución, evidencia de incidencias y cierre | RN-09 | US-09, US-10, US-11 (CA-09 a CA-11) | *Registrar inicio* -> *Documentar incidencias* -> *Firmar conformidad* (`[DO5]`) | `Incidencia`, `FirmaConformidad`, `OrdenServicioStateMachine`, `ServicioEjecucion`, `index.html` y `admin.html` | `test_us09_a_us11_y_us18_ejecucion_incidencia_cierre_y_facturacion` |
| **N-02:** Sincronización de ausencias con nómina | - | US-12, US-17 (CA-12, CA-17) | *Reportar ausencia y sustitución* -> `[DO4] Registro Nómina` | `AusenciaReportada` (Event), `ServicioExcepciones.reportar_ausencia`, `admin.html` (`/admin`) | `test_us12_a_us17_excepciones_penalizaciones_y_nomina` |
| **N-01, N-03:** Penalización por acceso denegado o cancelación | RN-04, RN-05 | US-13, US-16 (CA-13, CA-16) | Gateways `¿Cancelación previa?` (50%) y `¿Permite acceso?` (100%) | `CancelacionSinPenalizacionSpec`, `ClienteSuperaLimiteReprogramacionesSpec`, `AccesoDenegadoRegistrado` | `test_excepciones_acceso_denegado_cancelacion_y_nomina` |
| **N-04:** Extras en sitio y recálculo de superficie | RN-06, RN-07 | US-14, US-15 (CA-14, CA-15) | Gateway `¿Extra o mayor superficie?` -> *Cotizar y autorizar* | `ServicioExtra`, `OrdenDeServicio.solicitar_y_autorizar_extra`, `recalcular_por_superficie_mayor` | `test_us12_a_us17_excepciones_penalizaciones_y_nomina` |
| **N-03, N-06:** Facturación vinculada y KPIs gerenciales | RN-03, RN-09 | US-18, US-19 (CA-18, CA-19) | *Emitir factura vinculada* (`[DO6]`) -> *Tablero mensual de KPIs* | `ServicioCerrado` (Event), `/api/administracion/kpis`, `/api/estado`, `admin.html` (`/admin`) | `test_flujo_completo_cotizacion_descuento_y_autorizacion` |