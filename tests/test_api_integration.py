import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient

from src.domain.value_objects import DomainError
from src.domain.state_machines import EstadoCotizacion, EstadoOrdenServicio
from src.api.main import app, repo, srv_cotizacion, srv_programacion, srv_ejecucion, srv_excepciones

client = TestClient(app)

@pytest.fixture(autouse=True)
def limpiar_estado():
    repo.cotizaciones.clear()
    repo.ordenes.clear()
    repo.cambios_personal.clear()
    repo.registros_facturables.clear()
    repo.reprogramaciones_por_cliente.clear()
    for c in repo.cuadrillas.values():
        c.ventanas_asignadas.clear()
        c.estado = "Disponible"

def test_flujo_completo_cotizacion_descuento_y_autorizacion():
    # US-01 y US-02: Crear cotización de 240 m2 + 1h extra -> 5 horas-persona y 2 personas
    res = client.post("/api/cotizaciones", json={
        "cliente_nombre": "Empresa Alfa",
        "datos_contacto": "contacto@alfa.com",
        "ubicacion": "San Nicolás",
        "tipo_inmueble": "oficina",
        "superficie_m2": 240.0,
        "frecuencia": "quincenal",
        "extras": [{"horas": 1.0, "costo": 500.0}],
    })
    assert res.status_code == 200
    datos = res.json()
    folio = datos["folio"]
    assert datos["horas_persona_sugeridas"] == 5.0
    assert datos["personal_sugerido"] == 2

    # US-03: Descuento de 15% por coordinador es bloqueado (403) y pasa a Pendiente de autorización
    res_desc = client.patch(f"/api/cotizaciones/{folio}/descuento", json={
        "porcentaje": 15.0, "rol": "coordinador", "usuario": "coord_camila"
    })
    assert res_desc.status_code == 403
    assert repo.cotizaciones[folio].estado == EstadoCotizacion.PENDIENTE_AUTORIZACION

    # US-04: Gerencia autoriza descuento mayor al 10%
    res_aut = client.post(f"/api/cotizaciones/{folio}/autorizar")
    assert res_aut.status_code == 200
    assert res_aut.json()["estado"] == EstadoCotizacion.AUTORIZADA.value

    # US-05: Cliente acepta cotización y genera Orden de Servicio
    res_acep = client.post(f"/api/cotizaciones/{folio}/aceptar")
    assert res_acep.status_code == 200
    folio_orden = res_acep.json()["folio_orden"]

    # US-06 y US-07: Programar y asignar cuadrilla C-05
    res_prog = client.post(f"/api/ordenes/{folio_orden}/programar", json={
        "fecha_inicio_iso": "2026-11-20T09:00:00",
        "id_cuadrilla": "C-05",
    })
    assert res_prog.status_code == 200
    assert res_prog.json()["cuadrilla"] == "C-05"

    # US-09, US-10, US-11 y US-18: Iniciar, registrar incidencia con foto, cerrar con firma y generar facturable
    assert client.post(f"/api/ordenes/{folio_orden}/iniciar").status_code == 200
    assert client.post(f"/api/ordenes/{folio_orden}/incidencias", json={
        "tipo": "daño en mobiliario",
        "descripcion": "Persiana dañada",
        "fotos": ["https://cleanpro.mx/foto1.jpg"],
    }).status_code == 200
    res_cierre = client.post(f"/api/ordenes/{folio_orden}/cerrar", json={
        "nombre_firmante": "Ing. Roberto Garza",
        "conformidad": True,
    })
    assert res_cierre.status_code == 200
    assert res_cierre.json()["estado"] == EstadoOrdenServicio.CERRADA_CONFORMIDAD.value

    # US-19: Consultar KPIs gerenciales
    res_kpis = client.get("/api/administracion/kpis")
    assert res_kpis.status_code == 200
    assert res_kpis.json()["servicios_pendientes_facturar"] == 1

def test_excepciones_acceso_denegado_cancelacion_y_nomina():
    cot = srv_cotizacion.solicitar_cotizacion({
        "folio": "COT-900",
        "cliente_nombre": "Cliente Prueba",
        "datos_contacto": "8100000000",
        "ubicacion": "Santa Catarina",
        "tipo_inmueble": "casa",
        "superficie_m2": 150.0,
        "frecuencia": "unica",
    })
    orden = srv_cotizacion.aceptar_cotizacion(cot.folio)
    fecha_prog = datetime(2026, 11, 22, 9, 0)
    srv_programacion.programar_y_asignar(orden.folio, fecha_prog, "C-03")

    # US-12 y US-17: Reportar ausencia de personal hacia nómina
    cambio = srv_excepciones.reportar_ausencia(orden.folio, "J. Ramírez", "Incapacidad", "D. Nerio")
    assert cambio["integrante_entrante"] == "D. Nerio"

    # US-13 (RN-05): Acceso denegado cobra 100%
    srv_excepciones.registrar_acceso_denegado(orden.folio, "evidencia_puerta_cerrada.jpg")
    assert orden.estado == EstadoOrdenServicio.NO_EJECUTADO_CON_CARGO
    assert repo.registros_facturables[orden.folio]["monto"] == orden.precio_total.valor