"""Puerto (interfaz) de persistencia del dominio CleanPro.

La capa de aplicación depende de esta abstracción y no de una base de datos
concreta (Principio de Inversión de Dependencias - DIP). La infraestructura
ofrece dos implementaciones intercambiables:

* RepositorioEnMemoria   -> pruebas unitarias rápidas.
* RepositorioSQLAlchemy  -> SQLite (local) o PostgreSQL (Docker / Render).
"""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional

from src.domain.entities import Cliente, CotizacionFormal, Cuadrilla, OrdenDeServicio


class RepositorioCleanPro(ABC):
    # --- Clientes ---
    @abstractmethod
    def guardar_cliente(self, cliente: Cliente) -> None: ...

    @abstractmethod
    def obtener_cliente(self, cliente_id: str) -> Optional[Cliente]: ...

    # --- Cotizaciones (Aggregate Root de venta) ---
    @abstractmethod
    def guardar_cotizacion(self, cotizacion: CotizacionFormal) -> None: ...

    @abstractmethod
    def obtener_cotizacion(self, folio: str) -> Optional[CotizacionFormal]: ...

    @abstractmethod
    def listar_cotizaciones(self) -> List[CotizacionFormal]: ...

    @abstractmethod
    def siguiente_folio_cotizacion(self) -> str: ...

    # --- Órdenes de servicio (Aggregate Root operativo) ---
    @abstractmethod
    def guardar_orden(self, orden: OrdenDeServicio) -> None: ...

    @abstractmethod
    def obtener_orden(self, folio: str) -> Optional[OrdenDeServicio]: ...

    @abstractmethod
    def listar_ordenes(self) -> List[OrdenDeServicio]: ...

    # --- Cuadrillas ---
    @abstractmethod
    def guardar_cuadrilla(self, cuadrilla: Cuadrilla) -> None: ...

    @abstractmethod
    def obtener_cuadrilla(self, id_cuadrilla: str) -> Optional[Cuadrilla]: ...

    @abstractmethod
    def listar_cuadrillas(self) -> List[Cuadrilla]: ...

    # --- Registros administrativos (US-17, US-18) ---
    @abstractmethod
    def guardar_registro_facturable(self, registro: Dict) -> None: ...

    @abstractmethod
    def obtener_registro_facturable(self, folio_orden: str) -> Optional[Dict]: ...

    @abstractmethod
    def listar_registros_facturables(self) -> List[Dict]: ...

    @abstractmethod
    def guardar_cambio_personal(self, registro: Dict) -> None: ...

    @abstractmethod
    def listar_cambios_personal(self) -> List[Dict]: ...

    # --- Contador de reprogramaciones (RN-08) ---
    @abstractmethod
    def incrementar_reprogramaciones(self, cliente: str) -> int: ...

    # --- Utilidad para pruebas / reinicio de la demo ---
    @abstractmethod
    def limpiar(self) -> None: ...


CUADRILLAS_INICIALES = [
    ("C-03", ["J. Ramírez", "M. López"]),
    ("C-05", ["A. Garza", "P. Sánchez"]),
    ("C-07", ["R. Treviño", "L. Morales"]),
]


def crear_cuadrillas_iniciales() -> List[Cuadrilla]:
    return [Cuadrilla(id=cid, integrantes=list(integrantes)) for cid, integrantes in CUADRILLAS_INICIALES]
