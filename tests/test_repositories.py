"""Pruebas de integración de persistencia.

Las mismas pruebas (contrato del puerto RepositorioCleanPro) se ejecutan contra
el repositorio en memoria y contra la base de datos real con SQLAlchemy, para
demostrar que los adaptadores son intercambiables (Liskov / DIP).
"""
from datetime import datetime

import pytest

from src.domain.entities import Cliente
from src.domain.state_machines import EstadoCotizacion, EstadoOrdenServicio
from src.domain.value_objects import FirmaConformidad
from src.infrastructure import mappers
from src.infrastructure.repositories import RepositorioEnMemoria, crear_repositorio
from tests.helpers import Servicios
from tests.helpers import datos_cotizacion

INICIO = datetime(2026, 11, 20, 9, 0)


@pytest.fixture(params=["memoria", "sqlalchemy"])
def repositorio(request, tmp_path):
    if request.param == "memoria":
        return RepositorioEnMemoria()
    pytest.importorskip("sqlalchemy")
    from src.infrastructure.sqlalchemy_repository import RepositorioSQLAlchemy

    return RepositorioSQLAlchemy(f"sqlite:///{tmp_path / 'cleanpro_test.db'}")


def test_fabrica_elige_memoria():
    assert isinstance(crear_repositorio("memory"), RepositorioEnMemoria)


def test_cuadrillas_iniciales_y_limpieza(repositorio):
    assert [c.id for c in repositorio.listar_cuadrillas()] == ["C-03", "C-05", "C-07"]
    repositorio.guardar_cliente(Cliente("Ana", "81"))
    repositorio.limpiar()
    assert repositorio.obtener_cliente("81") is None
    assert len(repositorio.listar_cuadrillas()) == 3


def test_ciclo_completo_persistido(repositorio):
    srv = Servicios(repositorio)
    cot = srv.cotizacion.solicitar_cotizacion(datos_cotizacion(superficie_m2=150, datos_contacto="ana@correo.com"))
    assert repositorio.siguiente_folio_cotizacion() == "COT-1002"
    assert repositorio.obtener_cliente("ana@correo.com").contacto == "ana@correo.com"

    srv.cotizacion.aplicar_descuento(cot.folio, 5, "coordinador", "coord")
    orden = srv.cotizacion.aceptar_cotizacion(cot.folio)
    srv.programacion.programar_y_asignar(orden.folio, INICIO, "C-05")
    srv.excepciones.autorizar_servicio_extra(orden.folio, "Terraza", 300, True)
    srv.excepciones.reportar_ausencia(orden.folio, "A. Garza", "Enfermedad", "C. Nuevo")
    srv.ejecucion.registrar_inicio(orden.folio, INICIO)
    srv.ejecucion.documentar_incidencia(orden.folio, "daño", "Vidrio estrellado", ["f1.jpg", "f2.jpg"])
    srv.ejecucion.cerrar_servicio(orden.folio, "Ana", False, "Faltó la cocina")
    srv.administracion.facturar(orden.folio, "FAC-9")

    cot_guardada = repositorio.obtener_cotizacion(cot.folio)
    assert cot_guardada.estado == EstadoCotizacion.ACEPTADA
    assert cot_guardada.descuento.porcentaje == 5

    o = repositorio.obtener_orden(orden.folio)
    assert o.estado == EstadoOrdenServicio.FACTURADA
    assert o.folio_factura == "FAC-9"
    assert o.cuadrilla_asignada.integrantes == ["P. Sánchez", "C. Nuevo"]
    assert o.incidencias[0].fotos == ["f1.jpg", "f2.jpg"]
    assert o.extras[0].costo.valor == 300
    assert o.firma.motivo_inconformidad == "Faltó la cocina"
    assert o.hora_inicio_real == INICIO

    assert repositorio.listar_registros_facturables()[0]["folio_factura"] == "FAC-9"
    assert repositorio.listar_cambios_personal()[0]["integrante_entrante"] == "C. Nuevo"
    assert [x.folio for x in repositorio.listar_ordenes()] == [orden.folio]
    assert [x.folio for x in repositorio.listar_cotizaciones()] == [cot.folio]


def test_contador_de_reprogramaciones(repositorio):
    assert repositorio.incrementar_reprogramaciones("Ana|2026-11") == 1
    assert repositorio.incrementar_reprogramaciones("Ana|2026-11") == 2
    assert repositorio.incrementar_reprogramaciones("Ana|2026-12") == 1


def test_consultas_inexistentes(repositorio):
    assert repositorio.obtener_cotizacion("X") is None
    assert repositorio.obtener_orden("X") is None
    assert repositorio.obtener_cuadrilla("X") is None
    assert repositorio.obtener_registro_facturable("X") is None


def test_mapper_conserva_valores_guardados_aunque_cambie_la_tarifa():
    """Una cotización ya emitida no se recalcula al leerla, aunque cambie la configuración."""
    srv = Servicios(RepositorioEnMemoria())
    cot = srv.cotizacion.solicitar_cotizacion(datos_cotizacion())
    datos = mappers.cotizacion_a_dict(cot)
    datos["total"] = 1234.0
    assert mappers.dict_a_cotizacion(datos).total.valor == 1234.0


def test_mapper_firma_y_orden_sin_cuadrilla():
    srv = Servicios(RepositorioEnMemoria())
    cot = srv.cotizacion.solicitar_cotizacion(datos_cotizacion())
    orden = cot.aceptar_por_cliente()
    copia = mappers.dict_a_orden(mappers.orden_a_dict(orden), None)
    assert copia.firma is None and copia.cuadrilla_asignada is None and copia.monto_facturable is None
    firma = FirmaConformidad("Ana", True)
    orden.firma = firma
    assert mappers.dict_a_orden(mappers.orden_a_dict(orden), None).firma == firma


def test_normalizar_url_de_postgres():
    pytest.importorskip("sqlalchemy")
    from src.infrastructure.sqlalchemy_repository import normalizar_url

    assert normalizar_url("postgres://u:p@h/db") == "postgresql+psycopg2://u:p@h/db"
    assert normalizar_url("postgresql://u:p@h/db") == "postgresql+psycopg2://u:p@h/db"
    assert normalizar_url("sqlite:///./x.db") == "sqlite:///./x.db"
