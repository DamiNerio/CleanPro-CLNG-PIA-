"""Datos y utilidades de prueba reutilizables."""
from src.application.services import (
    ServicioAdministracion,
    ServicioCotizacion,
    ServicioEjecucion,
    ServicioExcepciones,
    ServicioProgramacion,
)


class Servicios:
    """Agrupa los casos de uso sobre un mismo repositorio."""

    def __init__(self, repo):
        self.repo = repo
        self.cotizacion = ServicioCotizacion(repo)
        self.programacion = ServicioProgramacion(repo)
        self.ejecucion = ServicioEjecucion(repo)
        self.excepciones = ServicioExcepciones(repo)
        self.administracion = ServicioAdministracion(repo)


def datos_cotizacion(**cambios):
    datos = {
        "cliente_nombre": "Cliente Prueba",
        "datos_contacto": "8100000000",
        "ubicacion": "San Nicolás, N.L.",
        "tipo_inmueble": "casa",
        "superficie_m2": 120.0,
        "frecuencia": "unica",
    }
    datos.update(cambios)
    return datos
