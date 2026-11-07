"""Adaptador de persistencia relacional con SQLAlchemy 2.0 (Core).

* Local / CI / pruebas: SQLite (archivo o en memoria).
* Docker Compose y Render: PostgreSQL (DATABASE_URL=postgresql://...).

Cada agregado se guarda en su propia tabla: las columnas que se consultan o
filtran (estado, cliente, cuadrilla, fecha) son columnas reales e indexadas, y
el detalle interno del agregado (incidencias, extras, firma, descuento) se guarda
en una columna JSON. Ver docs/architecture/ADRs.md (ADR-006).
"""
from typing import Dict, List, Optional

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Float,
    Integer,
    MetaData,
    String,
    Table,
    create_engine,
    delete,
    func,
    insert,
    select,
    update,
)
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool

from src.domain.entities import Cliente, CotizacionFormal, Cuadrilla, OrdenDeServicio
from src.domain.repositories import RepositorioCleanPro, crear_cuadrillas_iniciales
from src.infrastructure import mappers

metadata = MetaData()

clientes = Table(
    "clientes",
    metadata,
    Column("id", String(150), primary_key=True),
    Column("nombre", String(200), nullable=False),
    Column("contacto", String(200), nullable=False),
    Column("fecha_registro", DateTime, nullable=False),
)

cuadrillas = Table(
    "cuadrillas",
    metadata,
    Column("id", String(20), primary_key=True),
    Column("estado", String(30), nullable=False),
    Column("datos", JSON, nullable=False),
)

cotizaciones = Table(
    "cotizaciones",
    metadata,
    Column("folio", String(30), primary_key=True),
    Column("cliente_id", String(150), nullable=False, index=True),
    Column("estado", String(40), nullable=False, index=True),
    Column("total", Float, nullable=False),
    Column("fecha_creacion", DateTime, nullable=False),
    Column("datos", JSON, nullable=False),
)

ordenes_servicio = Table(
    "ordenes_servicio",
    metadata,
    Column("folio", String(30), primary_key=True),
    Column("folio_cotizacion", String(30), nullable=False),
    Column("cliente_id", String(150), nullable=False, index=True),
    Column("estado", String(40), nullable=False, index=True),
    Column("cuadrilla_id", String(20), nullable=True),
    Column("fecha_inicio_programada", DateTime, nullable=True),
    Column("datos", JSON, nullable=False),
)

registros_facturables = Table(
    "registros_facturables",
    metadata,
    Column("folio_orden", String(30), primary_key=True),
    Column("cliente", String(200), nullable=False),
    Column("monto", Float, nullable=False),
    Column("motivo", String(300), nullable=False),
    Column("folio_factura", String(60), nullable=True),
)

cambios_personal = Table(
    "cambios_personal",
    metadata,
    Column("id", String(20), primary_key=True),
    Column("folio_orden", String(30), nullable=False),
    Column("integrante_saliente", String(120), nullable=False),
    Column("integrante_entrante", String(120), nullable=False),
    Column("motivo", String(300), nullable=False),
    Column("fecha", String(40), nullable=False),
    Column("procesado_en_nomina", Boolean, nullable=False, default=False),
)

reprogramaciones = Table(
    "reprogramaciones",
    metadata,
    Column("clave", String(250), primary_key=True),
    Column("conteo", Integer, nullable=False),
)


def normalizar_url(database_url: str) -> str:
    """Render/Heroku entregan 'postgres://'; SQLAlchemy 2 necesita 'postgresql+psycopg2://'."""
    url = database_url.strip()
    if url.startswith("postgres://"):
        return "postgresql+psycopg2://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        return "postgresql+psycopg2://" + url[len("postgresql://"):]
    return url


def crear_engine(database_url: str) -> Engine:
    url = normalizar_url(database_url)
    if url.startswith("sqlite"):
        kwargs = {"connect_args": {"check_same_thread": False}}
        if url in ("sqlite://", "sqlite:///:memory:"):
            kwargs["poolclass"] = StaticPool  # una sola conexión compartida para la BD en memoria
        return create_engine(url, **kwargs)
    return create_engine(url, pool_pre_ping=True)


def _solo_columnas(tabla: Table, valores: Dict) -> Dict:
    return {k: v for k, v in valores.items() if k in tabla.c}


class RepositorioSQLAlchemy(RepositorioCleanPro):
    def __init__(self, database_url: str):
        self.engine = crear_engine(database_url)
        metadata.create_all(self.engine)
        self._sembrar_cuadrillas()

    # ------------------------------------------------------------ utilidades
    def _upsert(self, tabla: Table, pk: str, valores: Dict) -> None:
        valores = _solo_columnas(tabla, valores)
        with self.engine.begin() as conn:
            resultado = conn.execute(update(tabla).where(tabla.c[pk] == valores[pk]).values(**valores))
            if resultado.rowcount == 0:
                conn.execute(insert(tabla).values(**valores))

    def _uno(self, consulta):
        with self.engine.connect() as conn:
            return conn.execute(consulta).first()

    def _todos(self, consulta):
        with self.engine.connect() as conn:
            return conn.execute(consulta).all()

    def _sembrar_cuadrillas(self) -> None:
        with self.engine.connect() as conn:
            total = conn.execute(select(func.count()).select_from(cuadrillas)).scalar_one()
        if total == 0:
            for c in crear_cuadrillas_iniciales():
                self.guardar_cuadrilla(c)

    # ------------------------------------------------------------ clientes
    def guardar_cliente(self, cliente: Cliente) -> None:
        self._upsert(clientes, "id", {
            "id": cliente.id,
            "nombre": cliente.nombre,
            "contacto": cliente.contacto,
            "fecha_registro": cliente.fecha_registro,
        })

    def obtener_cliente(self, cliente_id: str) -> Optional[Cliente]:
        fila = self._uno(select(clientes).where(clientes.c.id == cliente_id))
        if not fila:
            return None
        return Cliente(nombre=fila.nombre, contacto=fila.contacto, fecha_registro=fila.fecha_registro)

    # ------------------------------------------------------------ cotizaciones
    def guardar_cotizacion(self, cotizacion: CotizacionFormal) -> None:
        self._upsert(cotizaciones, "folio", {
            "folio": cotizacion.folio,
            "cliente_id": Cliente.normalizar_contacto(cotizacion.datos_contacto),
            "estado": cotizacion.estado.value,
            "total": cotizacion.total.valor,
            "fecha_creacion": cotizacion.fecha_creacion,
            "datos": mappers.cotizacion_a_dict(cotizacion),
        })

    def obtener_cotizacion(self, folio: str) -> Optional[CotizacionFormal]:
        fila = self._uno(select(cotizaciones.c.datos).where(cotizaciones.c.folio == folio))
        return mappers.dict_a_cotizacion(fila.datos) if fila else None

    def listar_cotizaciones(self) -> List[CotizacionFormal]:
        filas = self._todos(select(cotizaciones.c.datos).order_by(cotizaciones.c.fecha_creacion, cotizaciones.c.folio))
        return [mappers.dict_a_cotizacion(f.datos) for f in filas]

    def siguiente_folio_cotizacion(self) -> str:
        with self.engine.connect() as conn:
            n = 1001 + conn.execute(select(func.count()).select_from(cotizaciones)).scalar_one()
            while conn.execute(select(cotizaciones.c.folio).where(cotizaciones.c.folio == f"COT-{n}")).first():
                n += 1
        return f"COT-{n}"

    # ------------------------------------------------------------ órdenes
    def guardar_orden(self, orden: OrdenDeServicio) -> None:
        self._upsert(ordenes_servicio, "folio", {
            "folio": orden.folio,
            "folio_cotizacion": orden.folio_cotizacion,
            "cliente_id": Cliente.normalizar_contacto(orden.datos_contacto),
            "estado": orden.estado.value,
            "cuadrilla_id": orden.cuadrilla_asignada.id if orden.cuadrilla_asignada else None,
            "fecha_inicio_programada": orden.fecha_inicio_programada,
            "datos": mappers.orden_a_dict(orden),
        })

    def obtener_orden(self, folio: str) -> Optional[OrdenDeServicio]:
        fila = self._uno(select(ordenes_servicio.c.datos).where(ordenes_servicio.c.folio == folio))
        if not fila:
            return None
        cuadrilla_id = fila.datos.get("cuadrilla_id")
        cuadrilla = self.obtener_cuadrilla(cuadrilla_id) if cuadrilla_id else None
        return mappers.dict_a_orden(fila.datos, cuadrilla)

    def listar_ordenes(self) -> List[OrdenDeServicio]:
        filas = self._todos(select(ordenes_servicio.c.datos).order_by(ordenes_servicio.c.folio))
        por_id = {c.id: c for c in self.listar_cuadrillas()}
        return [mappers.dict_a_orden(f.datos, por_id.get(f.datos.get("cuadrilla_id"))) for f in filas]

    # ------------------------------------------------------------ cuadrillas
    def guardar_cuadrilla(self, cuadrilla: Cuadrilla) -> None:
        self._upsert(cuadrillas, "id", {
            "id": cuadrilla.id,
            "estado": cuadrilla.estado,
            "datos": mappers.cuadrilla_a_dict(cuadrilla),
        })

    def obtener_cuadrilla(self, id_cuadrilla: str) -> Optional[Cuadrilla]:
        fila = self._uno(select(cuadrillas.c.datos).where(cuadrillas.c.id == id_cuadrilla))
        return mappers.dict_a_cuadrilla(fila.datos) if fila else None

    def listar_cuadrillas(self) -> List[Cuadrilla]:
        return [mappers.dict_a_cuadrilla(f.datos) for f in self._todos(select(cuadrillas.c.datos).order_by(cuadrillas.c.id))]

    # ------------------------------------------------------------ registros administrativos
    def guardar_registro_facturable(self, registro: Dict) -> None:
        self._upsert(registros_facturables, "folio_orden", registro)

    def obtener_registro_facturable(self, folio_orden: str) -> Optional[Dict]:
        fila = self._uno(select(registros_facturables).where(registros_facturables.c.folio_orden == folio_orden))
        return dict(fila._mapping) if fila else None

    def listar_registros_facturables(self) -> List[Dict]:
        return [dict(f._mapping) for f in self._todos(select(registros_facturables).order_by(registros_facturables.c.folio_orden))]

    def guardar_cambio_personal(self, registro: Dict) -> None:
        self._upsert(cambios_personal, "id", registro)

    def listar_cambios_personal(self) -> List[Dict]:
        return [dict(f._mapping) for f in self._todos(select(cambios_personal).order_by(cambios_personal.c.fecha))]

    def incrementar_reprogramaciones(self, cliente: str) -> int:
        fila = self._uno(select(reprogramaciones.c.conteo).where(reprogramaciones.c.clave == cliente))
        conteo = (fila.conteo if fila else 0) + 1
        self._upsert(reprogramaciones, "clave", {"clave": cliente, "conteo": conteo})
        return conteo

    # ------------------------------------------------------------ reinicio
    def limpiar(self) -> None:
        with self.engine.begin() as conn:
            for tabla in reversed(metadata.sorted_tables):
                conn.execute(delete(tabla))
        self._sembrar_cuadrillas()
