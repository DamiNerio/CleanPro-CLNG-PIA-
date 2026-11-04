from typing import Dict, List, Optional
from src.domain.entities import CotizacionFormal, OrdenDeServicio, Cuadrilla

class CleanProRepository:
    """Repositorio de infraestructura para persistencia de Agregados y Registros de Administración."""

    def __init__(self):
        self.cotizaciones: Dict[str, CotizacionFormal] = {}
        self.ordenes: Dict[str, OrdenDeServicio] = {}
        self.cuadrillas: Dict[str, Cuadrilla] = {
            "C-03": Cuadrilla(id="C-03", integrantes=["J. Ramírez", "M. López"]),
            "C-05": Cuadrilla(id="C-05", integrantes=["A. Garza", "P. Sánchez"]),
            "C-07": Cuadrilla(id="C-07", integrantes=["R. Treviño", "L. Morales"]),
        }
        self.cambios_personal: List[Dict] = []
        self.registros_facturables: Dict[str, Dict] = {}
        self.reprogramaciones_por_cliente: Dict[str, int] = {}

    def guardar_cotizacion(self, cotizacion: CotizacionFormal) -> None:
        self.cotizaciones[cotizacion.folio] = cotizacion

    def obtener_cotizacion(self, folio: str) -> Optional[CotizacionFormal]:
        return self.cotizaciones.get(folio)

    def guardar_orden(self, orden: OrdenDeServicio) -> None:
        self.ordenes[orden.folio] = orden

    def obtener_orden(self, folio: str) -> Optional[OrdenDeServicio]:
        return self.ordenes.get(folio)

    def obtener_cuadrilla(self, id_cuadrilla: str) -> Optional[Cuadrilla]:
        return self.cuadrillas.get(id_cuadrilla)

    def limpiar(self) -> None:
        self.cotizaciones.clear()
        self.ordenes.clear()
        self.cambios_personal.clear()
        self.registros_facturables.clear()
        self.reprogramaciones_por_cliente.clear()
        for c in self.cuadrillas.values():
            c.ventanas_asignadas.clear()
            c.estado = "Disponible"