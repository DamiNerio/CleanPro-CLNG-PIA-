"""Adaptador de persistencia en memoria y fábrica de repositorios.

RepositorioEnMemoria guarda los agregados ya serializados (igual que la base de
datos), así cada operación trabaja sobre una copia y las pruebas reflejan el
mismo comportamiento que tendrá RepositorioSQLAlchemy.
"""
import copy
from typing import Dict, List, Optional

from src.domain.entities import Cliente, CotizacionFormal, Cuadrilla, OrdenDeServicio
from src.domain.repositories import RepositorioCleanPro, crear_cuadrillas_iniciales
from src.infrastructure import mappers


class RepositorioEnMemoria(RepositorioCleanPro):
    def __init__(self):
        self.limpiar()

    # --- Clientes
    def guardar_cliente(self, cliente: Cliente) -> None:
        self._clientes[cliente.id] = mappers.cliente_a_dict(cliente)

    def obtener_cliente(self, cliente_id: str) -> Optional[Cliente]:
        d = self._clientes.get(cliente_id)
        return mappers.dict_a_cliente(d) if d else None

    # --- Cotizaciones
    def guardar_cotizacion(self, cotizacion: CotizacionFormal) -> None:
        self._cotizaciones[cotizacion.folio] = mappers.cotizacion_a_dict(cotizacion)

    def obtener_cotizacion(self, folio: str) -> Optional[CotizacionFormal]:
        d = self._cotizaciones.get(folio)
        return mappers.dict_a_cotizacion(copy.deepcopy(d)) if d else None

    def listar_cotizaciones(self) -> List[CotizacionFormal]:
        return [mappers.dict_a_cotizacion(copy.deepcopy(d)) for d in self._cotizaciones.values()]

    def siguiente_folio_cotizacion(self) -> str:
        n = 1001 + len(self._cotizaciones)
        while f"COT-{n}" in self._cotizaciones:
            n += 1
        return f"COT-{n}"

    # --- Órdenes
    def guardar_orden(self, orden: OrdenDeServicio) -> None:
        self._ordenes[orden.folio] = mappers.orden_a_dict(orden)

    def obtener_orden(self, folio: str) -> Optional[OrdenDeServicio]:
        d = self._ordenes.get(folio)
        if not d:
            return None
        return mappers.dict_a_orden(copy.deepcopy(d), self._cuadrilla_de(d))

    def listar_ordenes(self) -> List[OrdenDeServicio]:
        return [mappers.dict_a_orden(copy.deepcopy(d), self._cuadrilla_de(d)) for d in self._ordenes.values()]

    def _cuadrilla_de(self, d: Dict) -> Optional[Cuadrilla]:
        return self.obtener_cuadrilla(d["cuadrilla_id"]) if d.get("cuadrilla_id") else None

    # --- Cuadrillas
    def guardar_cuadrilla(self, cuadrilla: Cuadrilla) -> None:
        self._cuadrillas[cuadrilla.id] = mappers.cuadrilla_a_dict(cuadrilla)

    def obtener_cuadrilla(self, id_cuadrilla: str) -> Optional[Cuadrilla]:
        d = self._cuadrillas.get(id_cuadrilla)
        return mappers.dict_a_cuadrilla(copy.deepcopy(d)) if d else None

    def listar_cuadrillas(self) -> List[Cuadrilla]:
        return [mappers.dict_a_cuadrilla(copy.deepcopy(d)) for d in self._cuadrillas.values()]

    # --- Registros administrativos
    def guardar_registro_facturable(self, registro: Dict) -> None:
        self._facturables[registro["folio_orden"]] = dict(registro)

    def obtener_registro_facturable(self, folio_orden: str) -> Optional[Dict]:
        r = self._facturables.get(folio_orden)
        return dict(r) if r else None

    def listar_registros_facturables(self) -> List[Dict]:
        return [dict(r) for r in self._facturables.values()]

    def guardar_cambio_personal(self, registro: Dict) -> None:
        self._cambios_personal.append(dict(registro))

    def listar_cambios_personal(self) -> List[Dict]:
        return [dict(r) for r in self._cambios_personal]

    def incrementar_reprogramaciones(self, cliente: str) -> int:
        self._reprogramaciones[cliente] = self._reprogramaciones.get(cliente, 0) + 1
        return self._reprogramaciones[cliente]

    def limpiar(self) -> None:
        self._clientes: Dict[str, Dict] = {}
        self._cotizaciones: Dict[str, Dict] = {}
        self._ordenes: Dict[str, Dict] = {}
        self._cuadrillas: Dict[str, Dict] = {}
        self._facturables: Dict[str, Dict] = {}
        self._cambios_personal: List[Dict] = []
        self._reprogramaciones: Dict[str, int] = {}
        for c in crear_cuadrillas_iniciales():
            self.guardar_cuadrilla(c)


def crear_repositorio(database_url: str) -> RepositorioCleanPro:
    """Fábrica: elige el adaptador según DATABASE_URL (12-Factor App, config en el entorno)."""
    if database_url.strip().lower() in ("memory", "memoria"):
        return RepositorioEnMemoria()
    from src.infrastructure.sqlalchemy_repository import RepositorioSQLAlchemy  # import diferido

    return RepositorioSQLAlchemy(database_url)
