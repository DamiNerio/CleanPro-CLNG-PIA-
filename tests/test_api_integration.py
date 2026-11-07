"""Pruebas de integración de la API REST (FastAPI + base de datos real con SQLAlchemy).

Recorren el proceso completo del BPMN tal como lo hacen el portal del cliente (/)
y la intranet (/admin), y verifican la traducción de errores a códigos HTTP.
"""
import pytest

pytest.importorskip("fastapi")
pytest.importorskip("sqlalchemy")

from fastapi.testclient import TestClient  # noqa: E402

from src.api.main import app, repo  # noqa: E402

client = TestClient(app)

COTIZACION = {
    "cliente_nombre": "Empresa Alfa",
    "datos_contacto": "contacto@alfa.com",
    "ubicacion": "San Nicolás",
    "tipo_inmueble": "oficina",
    "superficie_m2": 240.0,
    "frecuencia": "quincenal",
    "extras": [{"horas": 1.0, "costo": 500.0}],
}


@pytest.fixture(autouse=True)
def base_limpia():
    repo.limpiar()
    yield
    repo.limpiar()


def crear_cotizacion(**cambios) -> str:
    res = client.post("/api/cotizaciones", json={**COTIZACION, **cambios})
    assert res.status_code == 200, res.text
    return res.json()["folio"]


def crear_orden_programada(fecha="2026-11-20T09:00:00", cuadrilla="C-05", **cambios) -> str:
    folio = crear_cotizacion(**cambios)
    folio_orden = client.post(f"/api/cotizaciones/{folio}/aceptar").json()["folio_orden"]
    res = client.post(f"/api/ordenes/{folio_orden}/programar", json={"fecha_inicio_iso": fecha, "id_cuadrilla": cuadrilla})
    assert res.status_code == 200, res.text
    return folio_orden


def test_vistas_web_y_health():
    assert "CleanPro" in client.get("/").text
    assert "Intranet" in client.get("/admin").text
    assert client.get("/health").json()["persistencia"] == "RepositorioSQLAlchemy"
    assert client.get("/openapi.json").status_code == 200


def test_flujo_completo_cliente_coordinador_gerencia_supervisor_administracion():
    # US-01 / US-02
    res = client.post("/api/cotizaciones", json=COTIZACION)
    datos = res.json()
    assert (datos["horas_persona_sugeridas"], datos["personal_sugerido"]) == (5.0, 2)
    folio = datos["folio"]

    # US-03: >10% por coordinador -> 403 y queda pendiente
    res = client.patch(f"/api/cotizaciones/{folio}/descuento", json={"porcentaje": 15.0, "rol": "coordinador", "usuario": "coord"})
    assert res.status_code == 403
    assert client.get(f"/api/cotizaciones/{folio}").json()["estado"] == "Pendiente de autorización"

    # US-04: gerencia autoriza
    res = client.post(f"/api/cotizaciones/{folio}/autorizar")
    assert res.json() == {"folio": folio, "estado": "Autorizada", "autorizado_por": "Lic. Renata Cárdenas"}

    # US-05 -> US-06/07
    folio_orden = client.post(f"/api/cotizaciones/{folio}/aceptar").json()["folio_orden"]
    res = client.post(f"/api/ordenes/{folio_orden}/programar", json={"fecha_inicio_iso": "2026-11-20T09:00:00", "id_cuadrilla": "C-05"})
    assert res.json()["cuadrilla"] == "C-05"

    # US-08: agenda del supervisor
    agenda = client.get("/api/agenda", params={"fecha": "2026-11-20"}).json()
    assert [s["folio"] for s in agenda["servicios"]] == [folio_orden]

    # US-09 / US-10 / US-11
    assert client.post(f"/api/ordenes/{folio_orden}/iniciar").status_code == 200
    res = client.post(f"/api/ordenes/{folio_orden}/incidencias", json={"tipo": "daño", "descripcion": "Persiana", "fotos": ["f.jpg"]})
    assert res.json()["total_incidencias"] == 1
    res = client.post(f"/api/ordenes/{folio_orden}/cerrar", json={"nombre_firmante": "Ing. Roberto Garza", "conformidad": True})
    assert res.json()["estado"] == "Cerrado con conformidad"

    # US-18 / US-19
    assert client.get("/api/administracion/kpis").json()["servicios_pendientes_facturar"] == 1
    res = client.post(f"/api/facturables/{folio_orden}/facturar", json={"folio_factura": "FAC-2026-0001"})
    assert res.json()["folio_factura"] == "FAC-2026-0001"
    estado = client.get("/api/estado").json()
    assert estado["ordenes"][0]["estado"] == "Facturada"
    assert estado["kpis"]["servicios_pendientes_facturar"] == 0


def test_portal_cliente_solo_ve_sus_solicitudes():
    crear_cotizacion(datos_contacto="81-1234-5678", cliente_nombre="Ana")
    crear_cotizacion(datos_contacto="otro@correo.com", cliente_nombre="Beto")
    res = client.get("/api/clientes/solicitudes", params={"contacto": "8112345678"})
    assert [c["cliente"] for c in res.json()["cotizaciones"]] == ["Ana"]


def test_cliente_rechaza_y_gerencia_descarta():
    folio = crear_cotizacion()
    assert client.post(f"/api/cotizaciones/{folio}/rechazar").json()["estado"] == "Rechazada"
    grande = crear_cotizacion(superficie_m2=500)
    assert client.post(f"/api/cotizaciones/{grande}/descartar").json()["estado"] == "Propuesta descartada"


def test_codigos_de_error_http():
    assert client.post("/api/cotizaciones/COT-404/aceptar").status_code == 404
    assert client.get("/api/ordenes/SRV-404").status_code == 404
    assert client.post("/api/cotizaciones", json={**COTIZACION, "superficie_m2": 0}).status_code == 422

    folio = crear_cotizacion()
    client.post(f"/api/cotizaciones/{folio}/aceptar")
    res = client.post(f"/api/cotizaciones/{folio}/aceptar")
    assert res.status_code == 409 and res.json()["tipo"] == "TransicionInvalida"

    crear_orden_programada(cuadrilla="C-03")
    folio2 = crear_cotizacion(datos_contacto="otro")
    orden2 = client.post(f"/api/cotizaciones/{folio2}/aceptar").json()["folio_orden"]
    res = client.post(f"/api/ordenes/{orden2}/programar", json={"fecha_inicio_iso": "2026-11-20T10:00:00", "id_cuadrilla": "C-03"})
    assert res.status_code == 409 and res.json()["tipo"] == "ConflictoDeAgenda"
    res = client.post(f"/api/ordenes/{orden2}/programar", json={"fecha_inicio_iso": "mañana", "id_cuadrilla": "C-07"})
    assert res.status_code == 422


def test_excepciones_operativas():
    folio_orden = crear_orden_programada(cuadrilla="C-03", superficie_m2=150, extras=[])

    # US-12 / US-17
    res = client.post(f"/api/ordenes/{folio_orden}/ausencia", json={"integrante_ausente": "J. Ramírez", "integrante_reemplazo": "D. Nerio", "motivo": "Incapacidad"})
    assert res.json()["integrante_entrante"] == "D. Nerio"
    assert "D. Nerio" in client.get("/api/cuadrillas").json()[0]["integrantes"]

    # US-14 / US-15
    res = client.post(f"/api/ordenes/{folio_orden}/extras", json={"descripcion": "Terraza", "costo": 250.0, "autorizado_por_cliente": True})
    assert res.json()["precio_total"] == 150 * 25 + 250
    res = client.post(f"/api/ordenes/{folio_orden}/ajuste-superficie", json={"nueva_superficie_m2": 200.0, "fotos": ["m2.jpg"], "autorizado_por_cliente": True})
    assert res.json()["superficie_m2"] == 200.0

    # US-16 / RN-08
    res = client.post(f"/api/ordenes/{folio_orden}/reprogramar", json={"nueva_fecha_iso": "2026-11-25T09:00:00", "fecha_solicitud_iso": "2026-11-10T09:00:00"})
    assert res.json()["reprogramaciones_mes"] == 1

    # US-13 / RN-05
    res = client.post(f"/api/ordenes/{folio_orden}/acceso-denegado", json={"evidencia": "puerta.jpg"})
    assert res.json()["estado"] == "No ejecutado con cargo"
    assert client.get("/api/estado").json()["facturables"][0]["monto"] == res.json()["cargo"]


def test_cancelacion_tardia_y_anticipada():
    tardia = crear_orden_programada(fecha="2026-11-20T09:00:00", cuadrilla="C-03")
    res = client.post(f"/api/ordenes/{tardia}/cancelar", json={"fecha_solicitud_iso": "2026-11-19T21:00:00"})
    assert res.json()["estado"] == "Cancelado con cargo" and res.json()["cargo"] > 0

    anticipada = crear_orden_programada(fecha="2030-01-10T09:00:00", cuadrilla="C-05", datos_contacto="otro")
    res = client.post(f"/api/ordenes/{anticipada}/cancelar")  # sin cuerpo: usa la hora actual
    assert res.json() == {"estado": "Cancelado sin cargo", "cargo": 0.0}


def test_acceso_denegado_sin_cuerpo_usa_evidencia_por_defecto():
    folio_orden = crear_orden_programada()
    assert client.post(f"/api/ordenes/{folio_orden}/acceso-denegado").status_code == 200
