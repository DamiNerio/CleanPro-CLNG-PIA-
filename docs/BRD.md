# Business Requirements Document (BRD) - Caso 12: CleanPro

**Universidad Autónoma de Nuevo León**  
**Facultad de Ingeniería Mecánica y Eléctrica (FIME)**  
**Unidad de Aprendizaje:** Componentes de Lógica de Negocios (CLN)  
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

**Oportunidad:** Digitalizar el ciclo completo de cotización-programación-asignación-ejecución-facturación mediante un sistema basado en lógica de negocio (DDD, Specification y State Machine) con reglas claras, trazabilidad de extremo a extremo y tableros de indicadores.

### 2.3 Stakeholders

| Rol | Participación Principal |
| :--- | :--- |
| **Cliente / Prospecto** | Solicita cotización, acepta o rechaza propuestas, autoriza extras o ajustes de superficie en sitio y firma digitalmente de conformidad o inconformidad. |
| **Coordinador** | Cotiza, programa fechas, asigna cuadrillas disponibles, autoriza descuentos de hasta 10%, gestiona reprogramaciones y cotiza extras o recálculos en sitio. |
| **Cuadrilla** | Ejecuta el servicio de limpieza conforme al alcance autorizado y reporta ausencias, extras solicitados o incidencias al supervisor. |
| **Supervisor** | Valida acceso al inmueble, registra marca de inicio y término, documenta incidencias con evidencia fotográfica, recaba firma digital y reporta cambios de personal. |
| **Administración** | Valida cargos por penalización, emite facturas vinculadas a órdenes cerradas y procesa los cambios de personal para nómina. |
| **Gerencia (Lic. Renata Cárdenas)** | Autoriza descuentos mayores al 10% y servicios que superen 300 m2 u $8,000 MXN, monitorea alertas de reprogramación y consulta KPIs. |

### 2.4 Alcance del Proyecto
* **Dentro del alcance:** Solicitud y cálculo de cotización, autorización por niveles de rol, programación y asignación de cuadrillas sin traslapes, ejecución y cierre con acta digital, gestión de excepciones (ausencia de personal, acceso denegado, extras en sitio, inmueble mayor a lo reportado, cancelaciones y reprogramaciones), registro de incidencias con evidencia, generación de registros facturables y avisos directos a nómina.
* **Fuera del alcance:** Cálculo contable de nómina bancaria, pasarela de cobro con tarjetas bancarias, contabilidad fiscal general ante el SAT y aplicación móvil nativa para clientes.

### 2.5 Necesidades del Negocio
* **N-01:** Reglas claras, automatizadas y parametrizables para descuentos, límites de cotización, cancelaciones y reprogramaciones.
* **N-02:** Canal estructurado para que los cambios de personal lleguen el mismo día a administración sin depender de WhatsApp.
* **N-03:** Vinculación obligatoria entre cada servicio cerrado (o penalizado) y su registro facturable correspondiente.
* **N-04:** Captura obligatoria de evidencia digital (fotografías, notas y firmas) en incidencias, ajustes de superficie y cierres de servicio.
* **N-05:** Límites jerárquicos de autorización claramente diferenciados entre Coordinador y Gerencia.
* **N-06:** Reportes e indicadores automáticos de cumplimiento de SLA, cotizaciones, incidencias y facturación pendiente.

### 2.6 Restricciones y Supuestos
* **Restricciones:** Los umbrales numéricos (10%, 300 m2, $8,000, 24 horas, 4 horas) se gestionan como variables de entorno configurables sujetas a confirmación con el stakeholder.
* **Supuestos:** CleanPro opera en una sola región metropolitana; cada cuadrilla atiende un único servicio a la vez; la firma digital del cliente en el acta de servicio tiene plena validez como evidencia de cierre.

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

* **CA-01.1:** El formulario captura ubicación, tipo de inmueble, superficie en m2, número de habitaciones o áreas, frecuencia, extras solicitados y datos de contacto.
* **CA-01.2:** El sistema impide enviar la solicitud si falta algún campo obligatorio e indica cuál es, sin borrar la información ya capturada.
* **CA-01.3:** La superficie sólo acepta valores numéricos mayores a cero (> 0).
* **CA-01.4:** Al enviarse, la solicitud recibe un folio único y queda registrada con fecha, hora y canal de origen (`web`, `WhatsApp` o `llamada`).
* **CA-01.5:** No se exige historial previo: un prospecto nuevo puede completar el flujo sin registro de cliente existente.

```gherkin
Característica: Solicitud de cotización en línea

  Escenario: Prospecto nuevo envía una solicitud completa
    Dado que soy un prospecto sin historial en CleanPro
    Y me encuentro en el formulario web de solicitud de cotización
    Cuando capturo ubicación, tipo de inmueble "casa", superficie de 120 m2, frecuencia quincenal, el extra "limpieza de vidrios" y mis datos de contacto
    Y envío la solicitud
    Entonces el sistema registra la solicitud con un folio único, fecha, hora y canal "web"
    Y muestra un acuse con el folio al prospecto
    Y la solicitud aparece en la bandeja de pendientes del coordinador

  Escenario: Solicitud incompleta o con superficie inválida
    Dado que estoy capturando una solicitud de cotización
    Cuando dejo vacío el campo de ubicación o ingreso una superficie menor o igual a 0
    Entonces el sistema no registra la solicitud
    Y señala el dato obligatorio faltante o inválido
```

#### US-02 - Sugerencia de duración y personal estimado (Coordinador)
> **Como** coordinador, **quiero** que el sistema me sugiera duración y personal estimado según el tamaño del inmueble y los extras, **para** agilizar la cotización.

* **CA-02.1:** Al abrir una solicitud, el sistema propone duración estimada en horas y número de personas a partir de la superficie, tipo de inmueble y extras.
* **CA-02.2:** Los parámetros de cálculo (rendimiento en m2 por persona-hora y tiempo por extra) son configurables mediante variables de entorno sin cambios de código.
* **CA-02.3:** El coordinador puede sobrescribir la sugerencia; el sistema conserva el valor sugerido, el valor final, el usuario y la fecha del ajuste.
* **CA-02.4:** Si falta algún dato necesario para el cálculo, se indica cuál es en lugar de mostrar una estimación en cero.

```gherkin
Característica: Sugerencia automática de recursos de limpieza

  Escenario: Sugerencia automática a partir del tamaño del inmueble
    Dado que el parámetro de rendimiento está configurado en 60 m2 por persona-hora
    Y el extra "limpieza de vidrios" suma 1 hora
    Cuando abro la cotización de un inmueble de 240 m2 con ese extra
    Entonces el sistema sugiere 5 horas-persona de trabajo
    Y propone una cuadrilla de 2 personas
    Y permite modificar la propuesta antes de generar la cotización
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
    Dado que tengo rol de coordinador
    Y estoy elaborando una cotización de $10,000 para un contrato de frecuencia semanal
    Cuando aplico un descuento de 8% con el motivo "contrato de frecuencia"
    Entonces el sistema acepta el descuento sin autorización adicional
    Y el total de la cotización queda en $9,200
    Y el descuento queda registrado con mi usuario y la fecha

  Escenario: Descuento fuera del límite del coordinador
    Dado que tengo rol de coordinador
    Cuando intento aplicar un descuento de 15%
    Entonces el sistema no aprueba directamente el descuento
    Y cambia la cotización a estado "Pendiente de autorización"
    Y me informa que los descuentos mayores a 10% requieren autorización de gerencia
```

#### US-04 - Alerta y autorización de descuentos mayores al 10% o límites excedidos (Gerencia)
> **Como** gerente, **quiero** recibir una alerta cuando una cotización requiera un descuento mayor al 10% o supere 300 m2 / $8,000, **para** autorizarla antes de enviarla al cliente.

* **CA-04.1:** Al solicitarse un descuento mayor al 10% (RN-01) o excederse 300 m2 / $8,000 (RN-02), el sistema crea una tarea de autorización y notifica a gerencia.
* **CA-04.2:** Mientras la solicitud está pendiente, la cotización permanece en estado `Pendiente de autorización` y no puede enviarse ni aceptarse.
* **CA-04.3:** La Gerencia puede autorizar o rechazar, con comentario obligatorio en caso de rechazo.
* **CA-04.4:** La resolución registra usuario, fecha y hora, y es consultable desde la cotización.
* **CA-04.5:** Al autorizarse, la cotización cambia a estado `Autorizada` y se habilita su envío.

```gherkin
Característica: Autorización gerencial de cotizaciones excepcionales

  Escenario: Gerencia autoriza el descuento solicitado
    Dado que el coordinador solicitó un descuento de 15% en la cotización COT-1042
    Y la cotización está en estado "Pendiente de autorización"
    Cuando la gerente autoriza la solicitud
    Entonces la cotización cambia a estado "Autorizada"
    Y el sistema habilita el envío al cliente
    Y registra quién autorizó, con fecha y hora

  Escenario: Intento de envío sin autorización
    Dado que la cotización COT-1042 está en estado "Pendiente de autorización"
    Cuando el coordinador intenta enviarla al cliente
    Entonces el sistema bloquea el envío
    Y muestra que falta la autorización de gerencia
```

#### US-05 - Aceptación o rechazo de la cotización por el cliente (Cliente)
> **Como** cliente, **quiero** aceptar o rechazar la cotización desde el mismo medio donde la solicité, **para** agilizar mi decisión.

* **CA-05.1:** El cliente puede aceptar o rechazar desde el mismo canal por el que solicitó la cotización.
* **CA-05.2:** La aceptación registra fecha, hora e identidad de quien acepta.
* **CA-05.3:** Una cotización aceptada genera automáticamente la Orden de Servicio asociada (RN-09).
* **CA-05.4:** Una cotización en estado `Aceptada` es inmutable: cualquier cambio posterior exige una nueva versión o ajuste en la orden.
* **CA-05.5:** El rechazo permite capturar un motivo opcional y cierra la cotización en estado `Rechazada` sin generar orden de servicio.

```gherkin
Característica: Resolución de la cotización por el cliente

  Escenario: El cliente acepta la cotización
    Dado que recibí la cotización COT-1042 por WhatsApp
    Cuando la acepto desde la liga recibida
    Entonces el sistema cambia la cotización a estado "Aceptada"
    Y genera automáticamente la orden de servicio correspondiente
    Y registra la fecha, la hora y mi identidad como aceptante

  Escenario: Cotización aceptada no editable
    Dado que la cotización COT-1042 está en estado "Aceptada"
    Cuando el coordinador intenta modificar el precio o descuento
    Entonces el sistema impide la edición
    Y solicita gestionar el cambio sobre la orden o crear una nueva versión
```

---

### Módulo 2: Programación y Asignación

#### US-06 - Programación de fecha y hora del servicio (Coordinador)
> **Como** coordinador, **quiero** programar fecha y hora del servicio una vez aceptada la cotización, **para** que quede agendado en el calendario del negocio.

* **CA-06.1:** Sólo pueden programarse órdenes provenientes de cotizaciones en estado `Aceptada`.
* **CA-06.2:** La programación exige fecha, hora de inicio y duración estimada.
* **CA-06.3:** El sistema bloquea la programación en un horario que ya está ocupado por la misma cuadrilla.
* **CA-06.4:** El servicio programado cambia a estado `Programada` y es visible para coordinador y supervisor.
* **CA-06.5:** Al programarse, se genera la confirmación para el cliente con fecha, hora y alcance.

```gherkin
Característica: Programación de órdenes de servicio

  Escenario: Programación válida de un servicio aceptado
    Dado que la cotización COT-1042 está aceptada y generó la orden SRV-1042
    Y no existe otro servicio traslapado el 20 de noviembre a las 09:00
    Cuando programo el servicio el 20 de noviembre a las 09:00 con duración de 5 horas
    Entonces el servicio cambia a estado "Programada" en el calendario
    Y el cliente recibe la confirmación con fecha, hora y alcance

  Escenario: Traslape de horarios
    Dado que la cuadrilla C-03 ya tiene un servicio el 20 de noviembre de 08:00 a 13:00
    Cuando intento programarle otro servicio el mismo día a las 11:00
    Entonces el sistema rechaza la programación
    Y muestra el conflicto de horario con la cuadrilla C-03
```

#### US-07 - Asignación de cuadrilla disponible (Coordinador)
> **Como** coordinador, **quiero** asignar una cuadrilla disponible a cada servicio programado, **para** evitar choques de horario o de personal.

* **CA-07.1:** El sistema sólo permite asignar cuadrillas con disponibilidad en la ventana de fecha y hora del servicio.
* **CA-07.2:** Una cuadrilla no puede quedar asignada a dos servicios traslapados.
* **CA-07.3:** La asignación registra la cuadrilla y sus integrantes en la orden de servicio.
* **CA-07.4:** Toda reasignación queda registrada en bitácora con usuario, fecha, hora y motivo.

```gherkin
Característica: Asignación de cuadrilla disponible

  Escenario: Asignación exitosa de cuadrilla sin traslape
    Dado que el servicio SRV-2210 está programado el 20 de noviembre de 09:00 a 14:00
    Y la cuadrilla C-05 no tiene servicios asignados en ese horario
    Cuando asigno la cuadrilla C-05 al servicio SRV-2210
    Entonces la orden de servicio muestra la cuadrilla C-05 y sus integrantes
    Y la cuadrilla C-05 queda reservada en esa ventana de tiempo
```

#### US-08 - Consulta de la agenda del día por el supervisor (Supervisor)
> **Como** supervisor, **quiero** ver en el sistema la cuadrilla y el detalle del servicio asignado para el día, **para** saber a dónde presentarme y qué se cotizó.

* **CA-08.1:** El supervisor consulta los servicios asignados a las cuadrillas que supervisa.
* **CA-08.2:** Cada servicio muestra folio, hora, dirección, cliente, superficie, alcance cotizado, extras autorizados e integrantes de la cuadrilla.
* **CA-08.3:** La información se expone mediante un endpoint REST consultable desde dispositivos móviles.
* **CA-08.4:** Cualquier reasignación de cuadrilla o personal realizada por el coordinador se refleja inmediatamente en la consulta.

```gherkin
Característica: Consulta de agenda operativa del supervisor

  Escenario: Actualización de la agenda tras una reasignación
    Dado que consulto mi agenda del día con el servicio SRV-2210
    Cuando el coordinador reasigna ese servicio a la cuadrilla C-07
    Y consulto nuevamente el detalle del servicio SRV-2210
    Entonces veo la cuadrilla C-07 y sus integrantes actualizados
```

---

### Módulo 3: Ejecución y Cierre

#### US-09 - Registro de hora de inicio y término del servicio (Supervisor)
> **Como** supervisor, **quiero** registrar la hora de inicio y término del servicio, **para** tener evidencia formal del tiempo real trabajado.

* **CA-09.1:** El registro de inicio y término utiliza la marca de tiempo del sistema y transiciona el estado de la orden a `En ejecución`.
* **CA-09.2:** La máquina de estados impide registrar el término o cierre si no existe previamente un registro de inicio (`En ejecución`).
* **CA-09.3:** El sistema calcula la duración real en horas y su diferencia contra la duración estimada.
* **CA-09.4:** Toda marca de tiempo queda almacenada en el Acta Digital de Servicio.

```gherkin
Característica: Control de tiempos de ejecución en sitio

  Escenario: Registro completo de la jornada
    Dado que soy el supervisor del servicio programado SRV-2210
    Cuando registro el inicio del servicio y posteriormente su término
    Entonces el sistema guarda ambas marcas de tiempo del sistema
    Y calcula la duración real comparándola contra la duración estimada

  Escenario: Intento de término sin inicio registrado
    Dado que el servicio SRV-2211 está en estado "Programada" sin hora de inicio
    Cuando intento registrar el cierre o término del servicio
    Entonces el sistema bloquea la operación
    Y me indica que primero debo registrar el inicio del servicio
```

#### US-10 - Registro de incidencias con evidencia digital (Supervisor)
> **Como** supervisor, **quiero** capturar fotos y notas de las incidencias ocurridas, **para** dejar evidencia digital en lugar de hojas de papel que se pierden.

* **CA-10.1:** Una incidencia se registra con tipo, descripción y al menos una fotografía de evidencia.
* **CA-10.2:** Cada evidencia guarda fecha y hora de captura y queda ligada a la orden de servicio.
* **CA-10.3:** Las incidencias son consultables inmediatamente por coordinador y administración.
* **CA-10.4:** El servicio no puede cerrarse si contiene incidencias registradas sin descripción o sin evidencia fotográfica.

```gherkin
Característica: Documentación digital de incidencias en sitio

  Escenario: Incidencia documentada con fotografía
    Dado que durante el servicio SRV-2210 se daña una persiana
    Cuando registro la incidencia de tipo "daño en mobiliario" con descripción y dos fotos
    Entonces la incidencia queda ligada al servicio SRV-2210
    Y el coordinador y administración pueden consultarla con sus evidencias

  Escenario: Intento de cierre con incidencia incompleta
    Dado que el servicio SRV-2210 tiene una incidencia registrada sin descripción
    Cuando intento cerrar el servicio
    Entonces el sistema bloquea el cierre
    Y señala que la incidencia debe tener descripción y evidencia completa
```

#### US-11 - Firma digital de conformidad del cliente (Cliente)
> **Como** cliente, **quiero** firmar digitalmente de conformidad al finalizar el servicio, **para** confirmar mi satisfacción o reportar inconformidad de inmediato.

* **CA-11.1:** Al finalizar, el sistema presenta el resumen del alcance ejecutado, los extras autorizados y las incidencias registradas.
* **CA-11.2:** La firma digital almacena el nombre de quien firma, fecha, hora y el indicador de conformidad.
* **CA-11.3:** Si el cliente manifiesta inconformidad, el sistema exige un motivo obligatorio y cambia el estado a `Cerrado con inconformidad`.
* **CA-11.4:** Si el cliente firma de conformidad, la orden pasa a estado `Cerrado con conformidad`.

```gherkin
Característica: Firma digital de cierre de servicio

  Escenario: Cierre con firma de conformidad
    Dado que el servicio SRV-2210 está en ejecución y tiene sus incidencias completas
    Cuando el cliente revisa el resumen y firma digitalmente de conformidad
    Entonces el servicio cambia a estado "Cerrado con conformidad"
    Y la firma queda almacenada en el acta digital con nombre, fecha y hora

  Escenario: Cliente inconforme
    Dado que el cliente no está satisfecho con el resultado del servicio SRV-2210
    Cuando registra su firma indicando inconformidad con el motivo "faltó limpieza de ventanas"
    Entonces el servicio cambia a estado "Cerrado con inconformidad"
    Y queda registrado el motivo obligatorio para seguimiento del coordinador
```

---

### Módulo 4: Excepciones Operativas

#### US-12 - Reporte de ausencia de un integrante de la cuadrilla (Supervisor)
> **Como** supervisor, **quiero** reportar la ausencia de un integrante de la cuadrilla el día del servicio, **para** que el coordinador reasigne personal o ajuste el equipo a tiempo.

* **CA-12.1:** El supervisor reporta la ausencia indicando orden de servicio, integrante ausente, motivo e integrante de reemplazo (si aplica).
* **CA-12.2:** La notificación se registra directamente en el sistema sin depender de mensajería informal.
* **CA-12.3:** Si hay reemplazo, se actualiza la lista de integrantes de la cuadrilla; si no, se registra la ejecución con equipo reducido.
* **CA-12.4:** El evento `AusenciaReportada` alimenta automáticamente la bandeja de cambios de personal de administración para nómina (US-17).

```gherkin
Característica: Gestión de ausencias de personal en cuadrilla

  Escenario: Se reporta ausencia y se asigna un reemplazo
    Dado que el integrante "J. Ramírez" no se presentó al servicio SRV-2210
    Cuando reporto la ausencia indicando el motivo y asignando al reemplazo "C. Nuevo"
    Entonces la cuadrilla actualiza sus integrantes para el servicio SRV-2210
    Y se genera automáticamente el registro de cambio de personal para administración
```

#### US-13 - Registro de acceso denegado al inmueble (Supervisor / Coordinador)
> **Como** coordinador, **quiero** registrar cuando un cliente no permite el acceso al inmueble, **para** aplicar la penalización correspondiente de forma consistente.

* **CA-13.1:** El supervisor registra el acceso denegado con hora de llegada y al menos una evidencia fotográfica o nota obligatoria.
* **CA-13.2:** El sistema aplica automáticamente el cargo del 100% del servicio conforme a la regla RN-05.
* **CA-13.3:** El servicio transiciona al estado `No ejecutado con cargo` y libera el horario de la cuadrilla para el resto de la jornada.
* **CA-13.4:** Se genera el registro facturable por el 100% para validación de administración.

```gherkin
Característica: Penalización por acceso denegado al inmueble

  Escenario: Acceso denegado con evidencia fotográfica
    Dado que la cuadrilla llegó al domicilio del servicio programado SRV-2215
    Y nadie permite el acceso al inmueble
    Cuando el supervisor registra "acceso denegado" adjuntando evidencia fotográfica
    Entonces el servicio cambia a estado "No ejecutado con cargo"
    Y el sistema genera un registro facturable por el 100% del monto cotizado
    Y libera la ventana de horario de la cuadrilla asignada
```

#### US-14 - Autorización de servicios adicionales solicitados en sitio (Cuadrilla / Coordinador)
> **Como** cuadrilla, **quiero** solicitar autorización al coordinador cuando el cliente pide un servicio adicional en sitio, **para** no realizar trabajo no cotizado sin aprobación.

* **CA-14.1:** La cuadrilla no puede agregar ni ejecutar por su cuenta trabajos no incluidos en la orden de servicio (RN-06).
* **CA-14.2:** El coordinador cotiza el servicio extra y solicita la confirmación del cliente.
* **CA-14.3:** Si el cliente autoriza el extra, la orden incorpora el trabajo y suma su costo al precio total antes de cerrarse.
* **CA-14.4:** Si el cliente rechaza el extra, la orden conserva intacto su alcance y precio original.

```gherkin
Característica: Autorización de servicios adicionales en sitio

  Escenario: Extra autorizado por el cliente
    Dado que el cliente solicita en sitio la limpieza de una terraza no cotizada
    Cuando el coordinador cotiza el extra en $900 y el cliente lo autoriza
    Entonces la orden de servicio incorpora el extra autorizado
    Y suma $900 al precio total del servicio

  Escenario: Extra rechazado por el cliente
    Dado que el coordinador cotizó un servicio extra en sitio por $900
    Cuando el cliente rechaza el costo del extra
    Entonces la orden de servicio conserva su alcance y precio original
```

#### US-15 - Recálculo de precio cuando el inmueble es mayor a lo reportado (Coordinador)
> **Como** coordinador, **quiero** recalcular el precio cuando el inmueble resulta más grande de lo reportado, **para** cobrar de forma justa y transparente.

* **CA-15.1:** El ajuste exige evidencia fotográfica obligatoria y una superficie real medida en sitio mayor a la cotizada (RN-07).
* **CA-15.2:** El sistema recalcula el precio de forma proporcional a la nueva superficie.
* **CA-15.3:** Si el cliente autoriza el ajuste, se actualiza la superficie y el precio total de la orden.
* **CA-15.4:** Si el cliente rechaza el ajuste, se mantiene la superficie y el precio originalmente cotizados.

```gherkin
Característica: Ajuste proporcional por superficie mayor en sitio

  Escenario: El cliente acepta el ajuste proporcional
    Dado que el servicio SRV-2210 se cotizó originalmente para 150 m2
    Y el supervisor mide 200 m2 reales en sitio y adjunta fotografías de evidencia
    Cuando el coordinador recalcula el precio de forma proporcional y el cliente acepta
    Entonces la orden de servicio actualiza su superficie a 200 m2
    Y el precio total aumenta proporcionalmente en un factor de 200/150

  Escenario: El cliente rechaza el ajuste de superficie
    Dado que el coordinador propuso el ajuste por superficie real de 200 m2
    Cuando el cliente rechaza el ajuste
    Entonces la orden conserva los 150 m2 y el precio originalmente cotizado
```

#### US-16 - Solicitud de reprogramación o cancelación por el cliente (Cliente)
> **Como** cliente, **quiero** solicitar una reprogramación o cancelación con anticipación, **para** evitar penalizaciones por cancelación tardía.

* **CA-16.1:** El sistema evalúa la anticipación respecto a la fecha y hora programada conforme a la regla RN-04.
* **CA-16.2:** Si faltan 24 horas o más (o existe causa de fuerza mayor autorizada), la cancelación cambia el estado a `Cancelado sin cargo` (0% de cobro).
* **CA-16.3:** Si faltan menos de 24 horas y no hay fuerza mayor, la cancelación cambia el estado a `Cancelado con cargo` y genera un registro facturable por el 50% del servicio.
* **CA-16.4:** Al cancelar o reprogramar, se libera la ventana original de la cuadrilla.
* **CA-16.5:** El sistema contabiliza las reprogramaciones del cliente en el mes y activa una alerta para gerencia cuando supera 2 reprogramaciones (RN-08).

```gherkin
Característica: Políticas de cancelación y reprogramación

  Escenario: Reprogramación con 24 horas o más de anticipación
    Dado que el servicio SRV-2210 está programado para el 20 de noviembre a las 09:00
    Y la solicitud se realiza el 18 de noviembre a las 10:00 (más de 24 horas antes)
    Cuando el cliente solicita reprogramarlo al 22 de noviembre a las 09:00
    Entonces el sistema reagenda el servicio sin cargo
    Y libera la cuadrilla de la fecha original

  Escenario: Cancelación tardía con menos de 24 horas
    Dado que el servicio SRV-2210 está programado para mañana a las 09:00
    Y faltan 12 horas para su inicio
    Cuando el cliente confirma la cancelación sin causa de fuerza mayor
    Entonces el servicio cambia a estado "Cancelado con cargo"
    Y el sistema genera un registro facturable por el 50% del monto del servicio
```

---

### Módulo 5: Administración y Reportes

#### US-17 - Llegada automática de los cambios de personal a administración (Administración)
> **Como** administración, **quiero** recibir automáticamente los cambios de personal registrados por el supervisor, **para** actualizar la nómina sin depender de mensajes informales.

* **CA-17.1:** Toda ausencia o sustitución registrada por el supervisor genera un registro estructurado con folio de servicio, fecha, integrante saliente, integrante entrante y motivo.
* **CA-17.2:** El registro aparece de inmediato en el tablero de administración sin intervención de WhatsApp.
* **CA-17.3:** Administración puede marcar cada cambio como `procesado_en_nomina = True` indicando el usuario que lo procesó.

```gherkin
Característica: Sincronización de cambios de personal con nómina

  Escenario: Cambio de personal disponible y procesado en nómina
    Dado que el supervisor registró una sustitución de personal en el servicio SRV-2210
    Cuando administración consulta la bandeja de cambios de personal pendientes
    Entonces visualiza el registro con el integrante saliente, entrante y motivo
    Y al marcarlo como procesado en nómina, deja de figurar como pendiente
```

#### US-18 - Vinculación entre servicio ejecutado y factura (Administración)
> **Como** administración, **quiero** que cada servicio finalizado quede vinculado a su factura correspondiente, **para** evitar servicios ejecutados y no cobrados.

* **CA-18.1:** Todo servicio que alcanza un estado de cierre (`Cerrado con conformidad` o `Cerrado con inconformidad`) o de penalización (`Cancelado con cargo` del 50% o `No ejecutado con cargo` del 100%) genera automáticamente un Registro Facturable (RN-09).
* **CA-18.2:** Cuando administración emite la factura fiscal, su folio queda vinculado al servicio y la orden transiciona al estado final `Facturada`.
* **CA-18.3:** El sistema permite listar en todo momento los servicios cerrados pendientes de facturar (cuya meta de negocio es llegar a cero).

```gherkin
Característica: Control de facturación vinculada a órdenes

  Escenario: Servicio cerrado genera registro facturable y se vincula a factura
    Dado que el servicio SRV-2210 se cerró con firma de conformidad
    Cuando administración consulta los registros pendientes de facturación
    Entonces el servicio SRV-2210 aparece con su monto final actualizado
    Y al vincularle el folio fiscal "FAC-9001", la orden cambia a estado "Facturada"
```

#### US-19 - Reportes e indicadores para la gerencia (Gerencia)
> **Como** gerente, **quiero** consultar reportes de cotizaciones cerradas, incidencias, cumplimiento de SLA y servicios pendientes de facturar, **para** tomar decisiones basadas en datos y no solo en percepción.

* **CA-19.1:** El endpoint de KPIs calcula automáticamente a partir de las entidades del sistema: total de cotizaciones por estado, porcentaje de cumplimiento del SLA de respuesta (menos de 4 horas hábiles, RN-03), total de incidencias, porcentaje de incidencias con evidencia digital, cambios de personal y servicios pendientes de facturar.
* **CA-19.2:** Los datos se obtienen en tiempo real sin recaptura manual en hojas de cálculo.

```gherkin
Característica: Tablero de indicadores clave de desempeño (KPIs)

  Escenario: Consulta de indicadores operativos y de facturación
    Dado que existen cotizaciones atendidas, servicios cerrados e incidencias registradas
    Cuando la gerente consulta el reporte de KPIs gerenciales
    Entonces el sistema devuelve el porcentaje de cumplimiento del SLA de 4 horas
    Y muestra la cantidad exacta de servicios pendientes de facturar y cambios de nómina
```

---

## 5. Glosario de Dominio (Lenguaje Ubicuo - 22 Términos)

| # | Término Ubicuo | Definición en el Dominio de CleanPro |
| :--- | :--- | :--- |
| 1 | **Prospecto** | Usuario que solicita una cotización inicial sin requerir historial previo en el sistema. |
| 2 | **Cliente** | Persona física o moral que acepta una cotización formal y recibe servicios de limpieza. |
| 3 | **Solicitud de Cotización** | Petición de entrada por canal web, WhatsApp o teléfono que contiene datos del inmueble, frecuencia y extras. |
| 4 | **Cotización Formal** | Raíz de agregado de la fase comercial que encapsula el cálculo de costos, recursos sugeridos, descuentos y autorizaciones. |
| 5 | **Coordinador** | Rol operativo facultado para cotizar servicios de hasta 300 m2 y $8,000, aplicar descuentos de hasta 10%, programar fechas y asignar cuadrillas. |
| 6 | **Autorización de Gerencia** | Aprobación explícita de la Lic. Renata Cárdenas requerida cuando un descuento supera el 10% o el servicio excede 300 m2 u $8,000. |
| 7 | **Contrato de Frecuencia** | Modalidad de servicio periódico (semanal, quincenal, mensual) elegible para descuentos comerciales. |
| 8 | **Orden de Servicio** | Raíz de agregado de la fase operativa creada automáticamente al aceptarse una cotización; controla la ejecución, excepciones y cierre. |
| 9 | **Cuadrilla** | Equipo de operarios de limpieza con identidad única que atiende un solo servicio a la vez sin traslape de horarios. |
| 10 | **Supervisor** | Responsable en sitio de validar el acceso al domicilio, registrar tiempos de inicio y fin, reportar ausencias y documentar incidencias. |
| 11 | **Rendimiento Persona-Hora** | Parámetro técnico configurable (m2 por hora) utilizado para estimar las horas-hombre y el tamaño de cuadrilla requerido. |
| 12 | **Servicio Extra en Sitio** | Trabajo adicional no incluido en la cotización original que el cliente solicita durante la visita y que exige cotización del coordinador y autorización previa. |
| 13 | **Ajuste por Superficie Mayor** | Recálculo proporcional del precio de la orden cuando el metraje real medido en sitio con evidencia fotográfica supera lo reportado por el cliente. |
| 14 | **Incidencia** | Suceso imprevisto ocurrido durante la ejecución del servicio (ej. daño en mobiliario) que exige tipo, descripción y evidencia fotográfica. |
| 15 | **Acceso Denegado** | Excepción operativa en la que el cliente no permite la entrada al inmueble a la cuadrilla en el horario programado, generando un cargo del 100%. |
| 16 | **Cancelación Tardía** | Cancelación solicitada por el cliente con menos de 24 horas de anticipación respecto al inicio programado, sujeta a un cargo del 50%. |
| 17 | **Fuerza Mayor** | Causa extraordinaria validada por el coordinador que exime al cliente del cargo del 50% en una cancelación tardía. |
| 18 | **Reprogramación Recurrente** | Condición que se activa cuando un mismo cliente acumula más de 2 reprogramaciones en un mes, disparando una alerta a gerencia. |
| 19 | **Cambio de Personal** | Registro estructurado de ausencia o sustitución de un integrante de cuadrilla que se envía directamente al tablero de administración para nómina. |
| 20 | **Acta Digital de Servicio** | Conjunto inmutable de datos de cierre de la orden compuesto por las marcas de tiempo reales, evidencias fotográficas y la firma digital del cliente. |
| 21 | **Firma de Conformidad** | Aprobación digital capturada por el cliente al cierre del servicio; si se registra como inconformidad, exige capturar un motivo obligatorio. |
| 22 | **Registro Facturable** | Obligación de cobro generada automáticamente al cerrar un servicio o aplicar una penalización (50% o 100%) para garantizar que ningún servicio escape a facturación. |