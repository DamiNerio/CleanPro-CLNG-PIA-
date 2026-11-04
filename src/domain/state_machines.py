from enum import Enum
from src.domain.value_objects import DomainError

class EstadoCotizacion(str, Enum):
    BORRADOR = "Borrador"
    PENDIENTE_AUTORIZACION = "Pendiente de autorización"
    AUTORIZADA = "Autorizada"
    RECHAZADA_GERENCIA = "Propuesta descartada"
    ENVIADA = "Enviada"
    ACEPTADA = "Aceptada"
    RECHAZADA_CLIENTE = "Rechazada"

class CotizacionStateMachine:
    TRANSICIONES = {
        EstadoCotizacion.BORRADOR: {
            EstadoCotizacion.PENDIENTE_AUTORIZACION,
            EstadoCotizacion.AUTORIZADA,
            EstadoCotizacion.ENVIADA,
            EstadoCotizacion.ACEPTADA,
            EstadoCotizacion.RECHAZADA_CLIENTE,
        },
        EstadoCotizacion.PENDIENTE_AUTORIZACION: {
            EstadoCotizacion.AUTORIZADA,
            EstadoCotizacion.RECHAZADA_GERENCIA,
        },
        EstadoCotizacion.AUTORIZADA: {
            EstadoCotizacion.ENVIADA,
            EstadoCotizacion.ACEPTADA,
            EstadoCotizacion.RECHAZADA_CLIENTE,
        },
        EstadoCotizacion.ENVIADA: {
            EstadoCotizacion.BORRADOR,
            EstadoCotizacion.ACEPTADA,
            EstadoCotizacion.RECHAZADA_CLIENTE,
        },
        EstadoCotizacion.ACEPTADA: set(),
        EstadoCotizacion.RECHAZADA_CLIENTE: set(),
        EstadoCotizacion.RECHAZADA_GERENCIA: set(),
    }

    @classmethod
    def transicionar(cls, estado_actual: EstadoCotizacion, estado_nuevo: EstadoCotizacion) -> EstadoCotizacion:
        if estado_nuevo not in cls.TRANSICIONES.get(estado_actual, set()):
            raise DomainError(f"Transición de cotización inválida: {estado_actual.value} -> {estado_nuevo.value}")
        return estado_nuevo

class EstadoOrdenServicio(str, Enum):
    GENERADA = "Generada"
    PROGRAMADA = "Programada"
    EN_EJECUCION = "En ejecución"
    PENDIENTE_CONFORMIDAD = "Pendiente de conformidad"
    CERRADA_CONFORMIDAD = "Cerrado con conformidad"
    CERRADA_INCONFORMIDAD = "Cerrado con inconformidad"
    CANCELADA_SIN_CARGO = "Cancelado sin cargo"
    CANCELADA_CON_CARGO = "Cancelado con cargo"
    NO_EJECUTADO_CON_CARGO = "No ejecutado con cargo"
    FACTURADA = "Facturada"

class OrdenServicioStateMachine:
    TRANSICIONES = {
        EstadoOrdenServicio.GENERADA: {
            EstadoOrdenServicio.PROGRAMADA,
            EstadoOrdenServicio.CANCELADA_SIN_CARGO,
        },
        EstadoOrdenServicio.PROGRAMADA: {
            EstadoOrdenServicio.PROGRAMADA,
            EstadoOrdenServicio.EN_EJECUCION,
            EstadoOrdenServicio.NO_EJECUTADO_CON_CARGO,
            EstadoOrdenServicio.CANCELADA_SIN_CARGO,
            EstadoOrdenServicio.CANCELADA_CON_CARGO,
        },
        EstadoOrdenServicio.EN_EJECUCION: {
            EstadoOrdenServicio.PENDIENTE_CONFORMIDAD,
            EstadoOrdenServicio.CERRADA_CONFORMIDAD,
            EstadoOrdenServicio.CERRADA_INCONFORMIDAD,
        },
        EstadoOrdenServicio.PENDIENTE_CONFORMIDAD: {
            EstadoOrdenServicio.CERRADA_CONFORMIDAD,
            EstadoOrdenServicio.CERRADA_INCONFORMIDAD,
        },
        EstadoOrdenServicio.CERRADA_CONFORMIDAD: {EstadoOrdenServicio.FACTURADA},
        EstadoOrdenServicio.CERRADA_INCONFORMIDAD: {EstadoOrdenServicio.FACTURADA},
        EstadoOrdenServicio.CANCELADA_CON_CARGO: {EstadoOrdenServicio.FACTURADA},
        EstadoOrdenServicio.NO_EJECUTADO_CON_CARGO: {EstadoOrdenServicio.FACTURADA},
        EstadoOrdenServicio.CANCELADA_SIN_CARGO: set(),
        EstadoOrdenServicio.FACTURADA: set(),
    }

    @classmethod
    def transicionar(cls, estado_actual: EstadoOrdenServicio, estado_nuevo: EstadoOrdenServicio) -> EstadoOrdenServicio:
        if estado_nuevo not in cls.TRANSICIONES.get(estado_actual, set()):
            raise DomainError(f"Transición de orden inválida: {estado_actual.value} -> {estado_nuevo.value}")
        return estado_nuevo