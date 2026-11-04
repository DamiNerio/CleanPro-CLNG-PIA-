# Diagramas de Arquitectura, DDD y UML (Docs-as-Code)

Este documento concentra los diagramas arquitectónicos del sistema **CleanPro** en formato **Mermaid** (renderizables nativamente en GitHub) y su correspondencia con los archivos interactivos de Draw.io incluidos en el repositorio (`BPMN CleanPro.html`, `diagrama_de_clases_uml.html` y `Diagrama secuencia 1.html`).

---

## 1. Diagrama de Clases del Dominio (DDD + Specification + State Machine)

Representa las Raíces de Agregado (`CotizacionFormal`, `OrdenDeServicio`), Entidades (`Cuadrilla`, `Incidencia`, `ServicioExtra`), Objetos de Valor (`Monto`, `Superficie`, `Descuento`, `FirmaConformidad`), Máquinas de Estado y Especificaciones.

```mermaid
classDiagram
    class CotizacionFormal {
        <<Aggregate Root>>
        +String folio
        +String cliente_nombre
        +String datos_contacto
        +String ubicacion
        +String tipo_inmueble
        +Superficie superficie
        +String frecuencia
        +EstadoCotizacion estado
        +Descuento descuento
        +Monto subtotal
        +Monto total
        +Float horas_persona_sugeridas
        +Int personal_sugerido
        +aplicar_descuento(porcentaje, rol, usuario)
        +autorizar_por_gerencia(usuario_gerencia)
        +enviar_al_cliente()
        +aceptar_por_cliente() OrdenDeServicio
    }

    class OrdenDeServicio {
        <<Aggregate Root>>
        +String folio
        +String folio_cotizacion
        +Superficie superficie
        +Monto precio_total
        +EstadoOrdenServicio estado
        +DateTime fecha_inicio_programada
        +DateTime hora_inicio_real
        +DateTime hora_fin_real
        +Monto monto_facturable
        +programar(fecha_inicio, cuadrilla)
        +registrar_inicio(marca_tiempo)
        +documentar_incidencia(tipo, descripcion, fotos)
        +solicitar_y_autorizar_extra(descripcion, costo, autorizado)
        +recalcular_por_superficie_mayor(nueva_superficie, fotos, autorizado)
        +registrar_acceso_denegado(evidencia_foto)
        +cancelar(fecha_solicitud, fuerza_mayor)
        +cerrar_servicio(firma, hora_fin)
    }

    class Cuadrilla {
        <<Entity>>
        +String id
        +List~String~ integrantes
        +String estado
        +esta_disponible(inicio, fin) Bool
        +asignar_horario(inicio, fin)
        +liberar_horario(inicio, fin)
    }

    class Incidencia {
        <<Entity>>
        +String tipo
        +String descripcion
        +List~String~ fotos
        +DateTime fecha_hora
        +validar_para_cierre()
    }

    class ServicioExtra {
        <<Entity>>
        +String descripcion
        +Monto costo
        +Bool autorizado_por_cliente
    }

    class Monto {
        <<Value Object>>
        +Float valor
        +aplicar_porcentaje(porcentaje) Monto
        +factor(proporcion) Monto
    }

    class Superficie {
        <<Value Object>>
        +Float metros_cuadrados
    }

    class Descuento {
        <<Value Object>>
        +Float porcentaje
        +String motivo
        +String usuario
    }

    class FirmaConformidad {
        <<Value Object>>
        +String nombre_firmante
        +Bool conformidad
        +String motivo_inconformidad
        +DateTime fecha_hora
    }

    class Specification~T~ {
        <<Interface>>
        +is_satisfied_by(candidate) Bool
    }

    class DescuentoAutorizablePorCoordinadorSpec {
        <<Specification RN-01>>
        +Float limite
        +is_satisfied_by(porcentaje) Bool
    }

    class CotizacionDentroDeLimiteCoordinadorSpec {
        <<Specification RN-02>>
        +Float max_m2
        +Float max_monto
        +is_satisfied_by(candidate) Bool
    }

    class CancelacionSinPenalizacionSpec {
        <<Specification RN-04>>
        +Int horas_minimas
        +is_satisfied_by(candidate) Bool
    }

    class CuadrillaDisponibleSpec {
        <<Specification CA-07.2>>
        +is_satisfied_by(candidate) Bool
    }

    CotizacionFormal "1" --> "0..1" OrdenDeServicio : genera al aceptarse (RN-09)
    CotizacionFormal *-- Superficie
    CotizacionFormal *-- Monto
    CotizacionFormal *-- Descuento
    CotizacionFormal ..> DescuentoAutorizablePorCoordinadorSpec : valida RN-01
    CotizacionFormal ..> CotizacionDentroDeLimiteCoordinadorSpec : valida RN-02

    OrdenDeServicio "1" --> "0..1" Cuadrilla : asignada a
    OrdenDeServicio *-- "0..*" Incidencia
    OrdenDeServicio *-- "0..*" ServicioExtra
    OrdenDeServicio *-- "0..1" FirmaConformidad
    OrdenDeServicio ..> CancelacionSinPenalizacionSpec : valida RN-04
    Cuadrilla ..> CuadrillaDisponibleSpec : valida traslapes

    Specification <|.. DescuentoAutorizablePorCoordinadorSpec
    Specification <|.. CotizacionDentroDeLimiteCoordinadorSpec
    Specification <|.. CancelacionSinPenalizacionSpec
    Specification <|.. CuadrillaDisponibleSpec
```

---

## 2. Diagramas de Máquina de Estados (State Machine Pattern)

### 2.1 Máquina de Estados de `CotizacionFormal`
Modela las reglas **RN-01**, **RN-02** y los criterios **CA-03.2**, **CA-04.2**, **CA-05.3** y **CA-05.4**.

```mermaid
stateDiagram-v2
    [*] --> Borrador : Solicitud recibida (US-01)
    Borrador --> Pendiente_Autorizacion : Descuento > 10% (RN-01) o > 300m2 / $8,000 (RN-02)
    Borrador --> Enviada : Dentro de límites del Coordinador
    Pendiente_Autorizacion --> Autorizada : Gerencia aprueba (US-04)
    Pendiente_Autorizacion --> Propuesta_Descartada : Gerencia rechaza
    Autorizada --> Enviada : Coordinador envía al cliente
    Enviada --> Aceptada : Cliente acepta (US-05 -> Genera Orden RN-09)
    Enviada --> Rechazada : Cliente rechaza
    Autorizada --> Aceptada : Cliente acepta directo
    Propuesta_Descartada --> [*]
    Rechazada --> [*]
    Aceptada --> [*] : Estado inmutable (CA-05.4)
```

### 2.2 Máquina de Estados de `OrdenDeServicio`
Modela las reglas **RN-04**, **RN-05**, **RN-09** y los criterios **CA-06.1**, **CA-09.2**, **CA-10.4**, **CA-11.2**, **CA-13.3**, **CA-16.2** y **CA-18.1**.

```mermaid
stateDiagram-v2
    [*] --> Generada : Evento CotizacionAceptada (RN-09)
    Generada --> Programada : Asignar fecha y cuadrilla sin traslape (US-06, US-07)
    Programada --> Programada : Reprogramación >= 24h (US-16, RN-08)
    Programada --> Cancelado_Sin_Cargo : Cancelación >= 24h o Fuerza Mayor (RN-04)
    Programada --> Cancelado_Con_Cargo : Cancelación < 24h (Cargo 50% RN-04)
    Programada --> No_Ejecutado_Con_Cargo : Acceso denegado con evidencia (Cargo 100% RN-05)
    Programada --> En_Ejecucion : Supervisor registra hora de inicio (US-09)
    En_Ejecucion --> Cerrado_Con_Conformidad : Incidencias completas + Firma conforme (US-10, US-11)
    En_Ejecucion --> Cerrado_Con_Inconformidad : Firma inconforme con motivo obligatorio (CA-11.3)
    
    Cerrado_Con_Conformidad --> Facturada : Administración vincula factura fiscal (US-18)
    Cerrado_Con_Inconformidad --> Facturada : Administración vincula factura fiscal (US-18)
    Cancelado_Con_Cargo --> Facturada : Administración factura penalización 50% (US-18)
    No_Ejecutado_Con_Cargo --> Facturada : Administración factura penalización 100% (US-18)
    
    Cancelado_Sin_Cargo --> [*]
    Facturada --> [*]
```

---

## 3. Diagramas de Secuencia de Casos de Uso Críticos

### 3.1 Secuencia 1: Descuento Mayor al 10% y Autorización de Gerencia (US-03, US-04, RN-01)

```mermaid
sequenceDiagram
    actor Coordinador
    participant SC as ServicioCotizacion
    participant CF as CotizacionFormal
    participant Spec as DescuentoCoordinadorSpec
    actor Gerencia

    Coordinador->>SC: aplicar_descuento(folio="COT-1042", porcentaje=15, rol="coordinador")
    SC->>CF: aplicar_descuento(15, "coordinador")
    CF->>Spec: is_satisfied_by(15)
    Spec-->>CF: False (Excede límite de 10%)
    CF->>CF: CotizacionStateMachine.transicionar(PENDIENTE_AUTORIZACION)
    CF-->>SC: DomainError("Requiere autorización de gerencia RN-01")
    SC-->>Coordinador: HTTP 403 - Estado: Pendiente de autorización
    
    Gerencia->>SC: autorizar_cotizacion(folio="COT-1042", usuario="Lic. Renata Cárdenas")
    SC->>CF: autorizar_por_gerencia("Lic. Renata Cárdenas")
    CF->>CF: CotizacionStateMachine.transicionar(AUTORIZADA)
    CF-->>SC: Cotización Autorizada (Total con 15% aplicado)
    SC-->>Gerencia: HTTP 200 - Estado: Autorizada (Habilitada para envío)
```

### 3.2 Secuencia 2: Ajuste de Superficie Mayor en Sitio con Evidencia (US-15, RN-07)

```mermaid
sequenceDiagram
    actor Supervisor
    participant SE as ServicioExcepciones
    participant OS as OrdenDeServicio
    actor Cliente

    Supervisor->>SE: ajustar_superficie(folio="SRV-2210", nueva_superficie=200, fotos=["evidencia.jpg"])
    SE->>OS: recalcular_por_superficie_mayor(200, ["evidencia.jpg"], autorizado_cliente)
    OS->>OS: Validar fotos no vacías y 200 > 150
    Cliente->>SE: Autoriza ajuste proporcional
    OS->>OS: factor = 200 / 150
    OS->>OS: Actualizar superficie (200 m2) y precio_total proporcional
    OS-->>SE: OrdenDeServicio actualizada
    SE-->>Supervisor: HTTP 200 - Nuevo alcance y precio autorizados
```

### 3.3 Secuencia 3: Cierre de Servicio con Firma Digital y Vinculación a Facturación (US-10, US-11, US-18, RN-09)

```mermaid
sequenceDiagram
    actor Supervisor
    actor Cliente
    participant SEj as ServicioEjecucion
    participant OS as OrdenDeServicio
    participant Repo as CleanProRepository
    actor Administracion

    Supervisor->>SEj: cerrar_servicio(folio="SRV-2210", firmante="Ing. Garza", conformidad=True)
    SEj->>OS: cerrar_servicio(FirmaConformidad)
    OS->>OS: Verificar hora_inicio_real != None (CA-09.2)
    OS->>OS: Validar que todas las Incidencias tengan descripción y foto (CA-10.4)
    OS->>OS: OrdenServicioStateMachine.transicionar(CERRADA_CONFORMIDAD)
    OS->>OS: Emitir evento ServicioCerrado
    OS-->>SEj: Orden cerrada con monto_facturable
    SEj->>Repo: Crear RegistroFacturable vinculado a "SRV-2210" (RN-09)
    SEj-->>Cliente: HTTP 200 - Acta Digital firmada
    
    Administracion->>Repo: vincular_factura(folio_orden="SRV-2210", folio_factura="FAC-9001")
    Repo->>OS: OrdenServicioStateMachine.transicionar(FACTURADA)
    Repo-->>Administracion: Servicio Facturado (0 fugas de facturación)
```

---

## 4. Trazabilidad del Modelo BPMN (`BPMN CleanPro.html`)

El diagrama BPMN completo del repositorio modela el proceso *Gestión Integral de Limpieza CleanPro (AS-IS Optimizado)* distribuido en **5 Swimlanes (Participantes)** y **6 Data Objects**:

1. **Carril Cliente:** Evento de inicio por mensaje (*Solicitud de cotización Web/WhatsApp/Tel*) -> *Revisar y responder cotización (US-05)* -> Gateway exclusivo de aceptación -> *Autorizar/Rechazar extra o mayor superficie (US-14, US-15)* -> *Firmar conformidad digital (US-11)*.
2. **Carril Coordinador:** *Capturar datos y sugerir recursos (US-01, US-02)* -> Gateway `¿>10% desc. o >300m2 / $8,000? (RN-01, RN-02)` -> *Emitir y enviar cotización (<4h RN-03)* -> *Programar fecha y asignar cuadrilla (US-06, US-07)* -> Gateway `¿Cancelación previa? (US-16, RN-04)` -> *Cotizar extra o recálculo en sitio (US-14, US-15)*.
3. **Carril Gerencia (Lic. Renata Cárdenas):** *Evaluar excepción de precio/dimensión (US-04)* -> Gateway de aprobación o descarte de propuesta.
4. **Carril Supervisor / Cuadrilla:** *Consultar agenda y presentarse en sitio (US-08)* -> *Reportar ausencia y sustitución (US-12)* -> Gateway `¿Permite acceso? (RN-05)` -> *Registrar acceso denegado (US-13)* o *Registrar hora de inicio (US-09)* -> Gateway `¿Extra o mayor superficie? (RN-06, RN-07)` -> *Ejecutar limpieza y documentar incidencias (US-10)* -> *Registrar hora fin y resumen digital (US-09, US-11)*.
5. **Carril Administración:** *Facturar penalización 50% (RN-04)* / *Facturar penalización 100% (RN-05)* / *Aplicar cambios directos a nómina (US-17)* / *Emitir factura vinculada al servicio cerrado (US-18, RN-09)* -> *Generar tablero mensual de KPIs (US-19)* -> Evento de fin *Servicio Facturado y Cerrado*.
6. **Data Objects Modelados:** `[DO1] Solicitud Cotización`, `[DO2] Cotización Formal`, `[DO3] Orden de Servicio`, `[DO4] Registro Nómina`, `[DO5] Acta Digital + Fotos`, `[DO6] Factura Fiscal`.