"""Pruebas de los casos de uso (Service Layer) sobre el repositorio en memoria.

Siguen el flujo del BPMN: cotización -> programación -> ejecución -> excepciones -> administración.
"""
from datetime import date, datetime, timedelta

import pytest

from src.application.services import RecursoNoEncontrado
from src.domain.exceptions import AutorizacionRequerida, ConflictoDeAgenda, DomainError
from src.domain.state_machines import EstadoCotizacion, EstadoOrdenServicio
from tests.helpers import datos_cotizacion

INICIO = datetime(2026, 11, 20, 9, 0)


def orden_programada(srv, cuadrilla="C-03", **datos):
    cot = srv.cotizacion.solicitar_cotizacion(datos_cotizacion(**datos))
    orden = srv.cotizacion.aceptar_cotizacion(cot.folio)
    srv.programacion.programar_y_asignar(orden.folio, INICIO, cuadrilla)
    return orden.folio


def test_us01_registra_cliente_y_asigna_folio_consecutivo(srv, repo):
    c1 = srv.cotizacion.solicitar_cotizacion(datos_cotizacion(datos_contacto="81-1111-2222"))
    c2 = srv.cotizacion.solicitar_cotizacion(datos_cotizacion(datos_contacto="8111112222"))
    assert (c1.folio, c2.folio) == ("COT-1001", "COT-1002")
    assert repo.obtener_cliente("8111112222").nombre == "Cliente Prueba"


def test_us03_us04_descuento_bloqueado_se_guarda_pendiente_y_gerencia_autoriza(srv, repo):
    cot = srv.cotizacion.solicitar_cotizacion(datos_cotizacion(superficie_m2=100))
    srv.cotizacion.aplicar_descuento(cot.folio, 8, "coordinador", "coord")
    assert repo.obtener_cotizacion(cot.folio).total.valor == 2300.0

    with pytest.raises(AutorizacionRequerida):
        srv.cotizacion.aplicar_descuento(cot.folio, 15, "coordinador", "coord")
    assert repo.obtener_cotizacion(cot.folio).estado == EstadoCotizacion.PENDIENTE_AUTORIZACION

    srv.cotizacion.autorizar_cotizacion(cot.folio, "Lic. Renata Cárdenas")
    guardada = repo.obtener_cotizacion(cot.folio)
    assert guardada.estado == EstadoCotizacion.AUTORIZADA
    assert guardada.autorizado_por_gerencia == "Lic. Renata Cárdenas"


def test_us04_gerencia_descarta_y_us05_cliente_rechaza(srv, repo):
    grande = srv.cotizacion.solicitar_cotizacion(datos_cotizacion(superficie_m2=500))
    srv.cotizacion.descartar_cotizacion(grande.folio, "Gerencia")
    assert repo.obtener_cotizacion(grande.folio).estado == EstadoCotizacion.RECHAZADA_GERENCIA

    normal = srv.cotizacion.solicitar_cotizacion(datos_cotizacion())
    srv.cotizacion.rechazar_cotizacion(normal.folio)
    assert repo.obtener_cotizacion(normal.folio).estado == EstadoCotizacion.RECHAZADA_CLIENTE


def test_folio_inexistente(srv):
    with pytest.raises(RecursoNoEncontrado):
        srv.cotizacion.aceptar_cotizacion("COT-NO-EXISTE")
    with pytest.raises(RecursoNoEncontrado):
        srv.ejecucion.registrar_inicio("SRV-NO-EXISTE")
    folio = orden_programada(srv)
    with pytest.raises(RecursoNoEncontrado):
        srv.programacion.programar_y_asignar(folio, INICIO, "C-99")


def test_us06_us07_us08_programacion_traslape_y_agenda(srv, repo):
    folio1 = orden_programada(srv, "C-03")
    cot2 = srv.cotizacion.solicitar_cotizacion(datos_cotizacion(datos_contacto="8122222222"))
    orden2 = srv.cotizacion.aceptar_cotizacion(cot2.folio)

    with pytest.raises(ConflictoDeAgenda):
        srv.programacion.programar_y_asignar(orden2.folio, INICIO + timedelta(hours=1), "C-03")
    srv.programacion.programar_y_asignar(orden2.folio, INICIO + timedelta(hours=1), "C-05")

    agenda = srv.programacion.agenda_del_dia(date(2026, 11, 20))
    assert [o.folio for o in agenda] == [folio1, orden2.folio]
    assert srv.programacion.agenda_del_dia(date(2026, 11, 21)) == []
    assert repo.obtener_cuadrilla("C-03").estado == "Asignada"
    assert len(srv.programacion.listar_cuadrillas()) == 3


def test_us09_us10_us11_us18_ejecucion_cierre_y_facturacion(srv, repo):
    folio = orden_programada(srv)
    with pytest.raises(DomainError, match="inicio"):
        srv.ejecucion.cerrar_servicio(folio, "Cliente", True)

    srv.ejecucion.registrar_inicio(folio, INICIO)
    srv.ejecucion.documentar_incidencia(folio, "daño en mobiliario", "Persiana rota", ["foto1.jpg"])
    srv.ejecucion.cerrar_servicio(folio, "Cliente Firmante", True)

    orden = repo.obtener_orden(folio)
    assert orden.estado == EstadoOrdenServicio.CERRADA_CONFORMIDAD
    assert orden.firma.nombre_firmante == "Cliente Firmante"
    assert len(orden.incidencias) == 1
    assert repo.obtener_registro_facturable(folio)["motivo"] == "Servicio ejecutado"

    registro = srv.administracion.facturar(folio, "FAC-2026-0001")
    assert registro["folio_factura"] == "FAC-2026-0001"
    assert repo.obtener_orden(folio).estado == EstadoOrdenServicio.FACTURADA


def test_us18_no_factura_sin_registro(srv):
    folio = orden_programada(srv)
    with pytest.raises(RecursoNoEncontrado):
        srv.administracion.facturar(folio, "FAC-1")


def test_us12_us17_ausencia_actualiza_cuadrilla_y_llega_a_nomina(srv, repo):
    folio = orden_programada(srv, "C-03")
    registro = srv.excepciones.reportar_ausencia(folio, "J. Ramírez", "Incapacidad", "D. Nerio")
    assert registro["integrante_entrante"] == "D. Nerio"
    assert repo.obtener_cuadrilla("C-03").integrantes == ["M. López", "D. Nerio"]

    sin_reemplazo = srv.excepciones.reportar_ausencia(folio, "M. López", "Permiso")
    assert sin_reemplazo["integrante_entrante"] == "Equipo reducido"
    assert [r["id"] for r in repo.listar_cambios_personal()] == ["NOM-1", "NOM-2"]


def test_us13_acceso_denegado_genera_cargo_100(srv, repo):
    folio = orden_programada(srv)
    srv.excepciones.registrar_acceso_denegado(folio, "puerta_cerrada.jpg")
    orden = repo.obtener_orden(folio)
    assert orden.estado == EstadoOrdenServicio.NO_EJECUTADO_CON_CARGO
    assert repo.obtener_registro_facturable(folio)["monto"] == orden.precio_total.valor
    assert repo.obtener_cuadrilla("C-03").ventanas_asignadas == []


def test_us14_us15_extra_y_superficie_se_persisten(srv, repo):
    folio = orden_programada(srv, superficie_m2=150)
    precio = repo.obtener_orden(folio).precio_total.valor
    srv.excepciones.autorizar_servicio_extra(folio, "Terraza", 600, True)
    srv.excepciones.ajustar_superficie(folio, 200, ["m2.jpg"], True)
    orden = repo.obtener_orden(folio)
    assert orden.extras[0].descripcion == "Terraza"
    assert orden.superficie.metros_cuadrados == 200
    assert orden.precio_total.valor == round((precio + 600) * 200 / 150, 2)


def test_us16_cancelacion_tardia_cobra_50(srv, repo):
    folio = orden_programada(srv)
    resultado = srv.excepciones.cancelar_o_reprogramar(folio, INICIO - timedelta(hours=12))
    orden = repo.obtener_orden(folio)
    assert orden.estado == EstadoOrdenServicio.CANCELADA_CON_CARGO
    assert resultado["cargo"] == round(orden.precio_total.valor * 0.5, 2)
    assert "50%" in repo.obtener_registro_facturable(folio)["motivo"]


def test_us16_cancelacion_anticipada_sin_cargo(srv, repo):
    folio = orden_programada(srv)
    resultado = srv.excepciones.cancelar_o_reprogramar(folio, INICIO - timedelta(days=2))
    assert resultado == {"estado": EstadoOrdenServicio.CANCELADA_SIN_CARGO.value, "cargo": 0.0}
    assert repo.obtener_registro_facturable(folio) is None


def test_us16_rn08_tercera_reprogramacion_del_mes_alerta_gerencia(srv, repo):
    folio = orden_programada(srv)
    solicitud = datetime(2026, 11, 10, 10, 0)
    for dia in (21, 22):
        r = srv.excepciones.cancelar_o_reprogramar(folio, solicitud, nueva_fecha=datetime(2026, 11, dia, 9, 0))
        assert r["alerta_gerencia_rn08"] is False
    r = srv.excepciones.cancelar_o_reprogramar(folio, solicitud, nueva_fecha=datetime(2026, 11, 23, 9, 0))
    assert r == {"estado": "Programada", "reprogramaciones_mes": 3, "alerta_gerencia_rn08": True}
    # La cuadrilla solo conserva el último horario.
    assert repo.obtener_cuadrilla("C-03").ventanas_asignadas[0][0] == datetime(2026, 11, 23, 9, 0)


def test_us19_kpis_y_portal_solo_muestra_lo_del_cliente(srv):
    folio = orden_programada(srv, datos_contacto="ana@correo.com", cliente_nombre="Ana")
    srv.cotizacion.solicitar_cotizacion(datos_cotizacion(datos_contacto="otro@correo.com", superficie_m2=400))
    srv.excepciones.registrar_acceso_denegado(folio, "foto.jpg")

    kpis = srv.administracion.kpis()
    assert kpis["total_cotizaciones"] == 2
    assert kpis["cotizaciones_aceptadas"] == 1
    assert kpis["tasa_conversion_pct"] == 50.0
    assert kpis["pendientes_autorizacion"] == 1
    assert kpis["servicios_pendientes_facturar"] == 1

    propias = srv.administracion.solicitudes_de_cliente(" ANA@correo.com ")
    assert [c.cliente_nombre for c in propias["cotizaciones"]] == ["Ana"]
    assert [o.folio for o in propias["ordenes"]] == [folio]


def test_kpis_sin_datos(srv):
    assert srv.administracion.kpis()["tasa_conversion_pct"] == 0.0
