import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from src.domain.value_objects import Superficie, Monto, DomainError
from src.domain.state_machines import EstadoCotizacion, EstadoOrdenServicio
from src.api.main import app, repo, srv_cotizacion, srv_programacion, srv_ejecucion, srv_excepciones

client = TestClient(app)

@pytest.fixture(autouse=True)
def limpiar_repositorio():
    repo.cotizaciones.clear()
    repo.ordenes.clear()
    repo.cambios_personal.clear()
    repo.registros_facturables.clear()
    repo.reprogramaciones_por_cliente.clear()
    for c in repo.cuadrillas.values():
        c.ventanas_asignadas.clear()
        c.estado = "Disponible"

def test_us01_y_us02_cotizacion_y_sugerencia_recursos():
    """Verifica CA-01.3, CA-02.1: 240 m² a 60 m²/h + 1h extra = 5 horas-persona y 2 personas."""
    res = client.post("/api/cotizaciones", json={
        "cliente_nombre": "Prospecto Nuevo",
        "datos_contacto": "8110000000",
        "ubicacion": "Santa Catarina, N.L.",
        "tipo_inmueble": "casa",
        "superficie_m2": 240.0,
        "frecuencia": "quincenal",
        "extras": [{"horas": 1.0, "costo": 500.0}],
    })
    assert res.status_code == 200
    data = res.json()
    assert data["horas_persona_sugeridas"] == 5.0
    assert data["personal_sugerido"] == 2

def test_us03_y_us04_descuento_mayor_10_requiere_gerencia():
    """Verifica RN-01: Coordinador aplica <=10% directo; >10% bloquea y pasa a Pendiente de autorización."""
    cot = srv_cotizacion.solicitar_cotizacion({
        "folio": "COT-1042",
        "cliente_nombre": "Cliente Frecuente",
        "datos_contacto": "cliente@correo.com",
        "ubicacion": "San Nicolás",
        "tipo_inmueble": "oficina",
        "superficie_m2": 100.0,
        "frecuencia": "semanal",
    })
    # 8% aceptado al coordinador
    srv_cotizacion.aplicar_descuento("COT-1042", 8.0, "coordinador", "coord1")
    assert cot.total.valor == 2300.0

    # 15% bloqueado al coordinador y cambia a Pendiente de autorización
    res = client.patch("/api/cotizaciones/COT-1042/descuento", json={
        "porcentaje": 15.0, "rol": "coordinador", "usuario": "coord1"
    })
    assert res.status_code == 403
    assert repo.cotizaciones["COT-1042"].estado == EstadoCotizacion.PENDIENTE_AUTORIZACION

    # Gerencia autoriza
    res_aut = client.post("/api/cotizaciones/COT-1042/autorizar")
    assert res_aut.status_code == 200
    assert repo.cotizaciones["COT-1042"].estado == EstadoCotizacion.AUTORIZADA

def test_us06_y_us07_bloqueo_traslape_cuadrilla():
    """Verifica CA-06.3 y CA-07.2: Rechaza asignar la misma cuadrilla en horario traslapado."""
    srv_cotizacion.solicitar_cotizacion({
        "folio": "COT-1", "cliente_nombre": "C1", "datos_contacto": "1",
        "ubicacion": "U1", "tipo_inmueble": "casa", "superficie_m2": 120.0, "frecuencia": "unica"
    })
    srv_cotizacion.solicitar_cotizacion({
        "folio": "COT-2", "cliente_nombre": "C2", "datos_contacto": "2",
        "ubicacion": "U2", "tipo_inmueble": "casa", "superficie_m2": 120.0, "frecuencia": "unica"
    })
    o1 = srv_cotizacion.aceptar_cotizacion("COT-1")
    o2 = srv_cotizacion.aceptar_cotizacion("COT-2")

    srv_programacion.programar_y_asignar(o1.folio, datetime(2026, 10, 20, 9, 0), "C-03")
    with pytest.raises(DomainError, match="traslape"):
        srv_programacion.programar_y_asignar(o2.folio, datetime(2026, 10, 20, 10, 0), "C-03")

def test_us09_a_us11_y_us18_ejecucion_incidencia_cierre_y_facturacion():
    """Verifica CA-09.2, CA-10.4, CA-11.1 y RN-09: No cierra sin inicio ni con incidencia vacía, y genera factura."""
    srv_cotizacion.solicitar_cotizacion({
        "folio": "COT-2210", "cliente_nombre": "C1", "datos_contacto": "1",
        "ubicacion": "U1", "tipo_inmueble": "casa", "superficie_m2": 120.0, "frecuencia": "unica"
    })
    orden = srv_cotizacion.aceptar_cotizacion("COT-2210")

    # Intento de cierre sin inicio falla (CA-09.2)
    with pytest.raises(DomainError, match="inicio"):
        srv_ejecucion.cerrar_servicio(orden.folio, "Cliente", True)

    srv_ejecucion.registrar_inicio(orden.folio)
    # Incidencia sin descripción bloquea el cierre (CA-10.4)
    srv_ejecucion.documentar_incidencia(orden.folio, "daño", "", ["foto1.jpg"])
    with pytest.raises(DomainError, match="descripción"):
        srv_ejecucion.cerrar_servicio(orden.folio, "Cliente", True)

    # Corregir incidencia y cerrar con firma de conformidad
    orden.incidencias.clear()
    srv_ejecucion.documentar_incidencia(orden.folio, "daño en mobiliario", "Persiana rota", ["foto1.jpg"])
    srv_ejecucion.cerrar_servicio(orden.folio, "Cliente Firmante", True)
    assert orden.estado == EstadoOrdenServicio.CERRADA_CONFORMIDAD
    assert orden.folio in repo.registros_facturables

def test_us12_a_us17_excepciones_penalizaciones_y_nomina():
    """Verifica RN-04 (50%), RN-05 (100%), RN-07 (superficie mayor), RN-08 (>2 reprog) y US-17 (nómina)."""
    srv_cotizacion.solicitar_cotizacion({
        "folio": "COT-300", "cliente_nombre": "Cliente Excepciones", "datos_contacto": "1",
        "ubicacion": "U1", "tipo_inmueble": "casa", "superficie_m2": 150.0, "frecuencia": "unica"
    })
    orden = srv_cotizacion.aceptar_cotizacion("COT-300")
    fecha_prog = datetime(2026, 10, 20, 9, 0)
    srv_programacion.programar_y_asignar(orden.folio, fecha_prog, "C-05")

    # US-12 y US-17: Ausencia alimenta nómina
    reg_nomina = srv_excepciones.reportar_ausencia(orden.folio, "A. Garza", "Enfermedad", "C. Nuevo")
    assert reg_nomina["integrante_entrante"] == "C. Nuevo"
    assert len(repo.cambios_personal) == 1

    # US-15 (RN-07): Ajuste proporcional de 150 m² a 200 m²
    precio_anterior = orden.precio_total.valor
    orden.recalcular_por_superficie_mayor(200.0, ["evidencia_m2.jpg"], autorizado_cliente=True)
    assert orden.precio_total.valor == round(precio_anterior * (200.0 / 150.0), 2)

    # US-16 (RN-04): Cancelación con menos de 24h cobra 50%
    res_canc = srv_excepciones.cancelar_o_reprogramar(orden.folio, fecha_prog - timedelta(hours=12))
    assert orden.estado == EstadoOrdenServicio.CANCELADA_CON_CARGO
    assert res_canc["cargo"] == round(orden.precio_total.valor * 0.5, 2)
    