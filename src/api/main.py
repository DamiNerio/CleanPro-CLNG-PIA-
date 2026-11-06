from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from src.domain.value_objects import DomainError
from src.application.services import (
    CleanProRepository,
    ServicioCotizacion,
    ServicioProgramacion,
    ServicioEjecucion,
    ServicioExcepciones,
)

app = FastAPI(
    title="CleanPro - API de Lógica de Negocios (PIA CLNG)",
    description="Implementación DDD + Specification + State Machine para el Caso 12 CleanPro (Equipo 12 - FIME UANL).",
    version="1.0.0",
)

repo = CleanProRepository()
srv_cotizacion = ServicioCotizacion(repo)
srv_programacion = ServicioProgramacion(repo)
srv_ejecucion = ServicioEjecucion(repo)
srv_excepciones = ServicioExcepciones(repo)

class SolicitudCotizacionDTO(BaseModel):
    cliente_nombre: str = Field(..., example="Empresa Alfa S.A.")
    datos_contacto: str = Field(..., example="contacto@alfa.com")
    ubicacion: str = Field(..., example="Av. Universidad, San Nicolás")
    tipo_inmueble: str = Field(..., example="oficina")
    superficie_m2: float = Field(..., example=240.0)
    frecuencia: str = Field(..., example="quincenal")
    extras: List[Dict[str, float]] = Field(default_factory=list, example=[{"horas": 1.0, "costo": 450.0}])
    canal_origen: str = Field(default="web")

class DescuentoDTO(BaseModel):
    porcentaje: float = Field(..., example=8.0)
    rol: str = Field(..., example="coordinador")
    usuario: str = Field(..., example="coord_camila")
    motivo: str = Field(default="Contrato de frecuencia")

class ProgramacionDTO(BaseModel):
    fecha_inicio_iso: str = Field(..., example="2026-11-20T09:00:00")
    id_cuadrilla: str = Field(..., example="C-05")

class IncidenciaDTO(BaseModel):
    tipo: str = Field(..., example="daño en mobiliario")
    descripcion: str = Field(..., example="Persiana dañada en sala de juntas")
    fotos: List[str] = Field(..., example=["https://cleanpro.mx/evidencias/foto1.jpg"])

class CierreDTO(BaseModel):
    nombre_firmante: str = Field(..., example="Ing. Roberto Garza")
    conformidad: bool = Field(default=True)
    motivo_inconformidad: str = Field(default="")

class AusenciaDTO(BaseModel):
    integrante_ausente: str
    integrante_reemplazo: Optional[str] = None
    motivo: str

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def interfaz_web_cleanpro():
    html_path = Path(__file__).parent / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))

@app.get("/admin", response_class=HTMLResponse, include_in_schema=False)
def intranet_administrativa_cleanpro():
    html_path = Path(__file__).parent / "admin.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))

@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def interfaz_web_cleanpro():
    html_path = Path(__file__).parent / "index.html"
    return HTMLResponse(content=html_path.read_text(encoding="utf-8"))

@app.get("/api/estado", tags=["4. Administración y Reportes"])
def obtener_estado_completo():
    sin_facturar = [r for r in repo.registros_facturables.values() if not r["folio_factura"]]
    return {
        "kpis": {
            "total_cotizaciones": len(repo.cotizaciones),
            "total_ordenes": len(repo.ordenes),
            "servicios_pendientes_facturar": len(sin_facturar),
            "cambios_personal_registrados": len(repo.cambios_personal),
        },
        "cotizaciones": [
            {
                "folio": c.folio,
                "cliente": c.cliente_nombre,
                "superficie_m2": c.superficie.metros_cuadrados,
                "descuento": c.descuento.porcentaje,
                "total": c.total.valor,
                "estado": c.estado.value,
                "horas_sugeridas": c.horas_persona_sugeridas,
                "personal_sugerido": c.personal_sugerido,
            }
            for c in repo.cotizaciones.values()
        ],
        "ordenes": [
            {
                "folio": o.folio,
                "cliente": o.cliente_nombre,
                "superficie_m2": o.superficie.metros_cuadrados,
                "precio_total": o.precio_total.valor,
                "estado": o.estado.value,
                "cuadrilla": o.cuadrilla_asignada.id if o.cuadrilla_asignada else None,
                "incidencias": len(o.incidencias),
            }
            for o in repo.ordenes.values()
        ],
        "facturables": list(repo.registros_facturables.values()),
        "cambios_personal": repo.cambios_personal,
    }

@app.post("/api/cotizaciones", tags=["1. Cotización"])
def crear_cotizacion(dto: SolicitudCotizacionDTO):
    try:
        cot = srv_cotizacion.solicitar_cotizacion(dto.model_dump())
        return {
            "folio": cot.folio,
            "estado": cot.estado.value,
            "subtotal": cot.subtotal.valor,
            "total": cot.total.valor,
            "horas_persona_sugeridas": cot.horas_persona_sugeridas,
            "personal_sugerido": cot.personal_sugerido,
        }
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.patch("/api/cotizaciones/{folio}/descuento", tags=["1. Cotización"])
def aplicar_descuento(folio: str, dto: DescuentoDTO):
    if folio not in repo.cotizaciones:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    try:
        cot = srv_cotizacion.aplicar_descuento(folio, dto.porcentaje, dto.rol, dto.usuario, dto.motivo)
        return {"folio": cot.folio, "estado": cot.estado.value, "total": cot.total.valor}
    except DomainError as e:
        raise HTTPException(status_code=403, detail=str(e))

@app.post("/api/cotizaciones/{folio}/autorizar", tags=["1. Cotización"])
def autorizar_gerencia(folio: str, usuario_gerencia: str = "Lic. Renata Cárdenas"):
    if folio not in repo.cotizaciones:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    try:
        cot = srv_cotizacion.autorizar_cotizacion(folio, usuario_gerencia)
        return {"folio": cot.folio, "estado": cot.estado.value, "autorizado_por": cot.autorizado_por_gerencia}
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/cotizaciones/{folio}/aceptar", tags=["1. Cotización"])
def aceptar_cotizacion(folio: str):
    if folio not in repo.cotizaciones:
        raise HTTPException(status_code=404, detail="Cotización no encontrada")
    try:
        orden = srv_cotizacion.aceptar_cotizacion(folio)
        return {"folio_cotizacion": folio, "folio_orden": orden.folio, "estado_orden": orden.estado.value}
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/ordenes/{folio_orden}/programar", tags=["2. Programación y Asignación"])
def programar_orden(folio_orden: str, dto: ProgramacionDTO):
    if folio_orden not in repo.ordenes:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    try:
        fecha = datetime.fromisoformat(dto.fecha_inicio_iso)
        orden = srv_programacion.programar_y_asignar(folio_orden, fecha, dto.id_cuadrilla)
        return {
            "folio_orden": orden.folio,
            "estado": orden.estado.value,
            "cuadrilla": orden.cuadrilla_asignada.id,
            "integrantes": orden.cuadrilla_asignada.integrantes,
        }
    except DomainError as e:
        raise HTTPException(status_code=409, detail=str(e))

@app.post("/api/ordenes/{folio_orden}/iniciar", tags=["3. Ejecución"])
def iniciar_servicio(folio_orden: str):
    try:
        orden = srv_ejecucion.registrar_inicio(folio_orden)
        return {"folio_orden": orden.folio, "estado": orden.estado.value, "hora_inicio": orden.hora_inicio_real}
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/ordenes/{folio_orden}/incidencias", tags=["3. Ejecución"])
def registrar_incidencia(folio_orden: str, dto: IncidenciaDTO):
    try:
        orden = srv_ejecucion.documentar_incidencia(folio_orden, dto.tipo, dto.descripcion, dto.fotos)
        return {"folio_orden": orden.folio, "total_incidencias": len(orden.incidencias)}
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/ordenes/{folio_orden}/cerrar", tags=["3. Ejecución"])
def cerrar_servicio(folio_orden: str, dto: CierreDTO):
    try:
        orden = srv_ejecucion.cerrar_servicio(folio_orden, dto.nombre_firmante, dto.conformidad, dto.motivo_inconformidad)
        return {
            "folio_orden": orden.folio,
            "estado": orden.estado.value,
            "monto_facturable": orden.monto_facturable.valor,
        }
    except DomainError as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/ordenes/{folio_orden}/ausencia", tags=["3. Ejecución"])
def reportar_ausencia_endpoint(folio_orden: str, dto: AusenciaDTO):
    return srv_excepciones.reportar_ausencia(
        folio_orden, dto.integrante_ausente, dto.motivo, dto.integrante_reemplazo
    )

@app.post("/api/ordenes/{folio_orden}/acceso-denegado", tags=["3. Ejecución"])
def acceso_denegado_endpoint(folio_orden: str):
    orden = srv_excepciones.registrar_acceso_denegado(folio_orden, "evidencia_acceso_denegado.jpg")
    return {"folio_orden": orden.folio, "estado": orden.estado.value, "cargo": orden.monto_facturable.valor}

@app.post("/api/ordenes/{folio_orden}/cancelar", tags=["3. Ejecución"])
def cancelar_orden_endpoint(folio_orden: str):
    orden = repo.ordenes[folio_orden]
    fecha_ref = (orden.fecha_inicio_programada - timedelta(hours=12)) if orden.fecha_inicio_programada else datetime.utcnow()
    return srv_excepciones.cancelar_o_reprogramar(folio_orden, fecha_solicitud=fecha_ref)

@app.get("/api/administracion/kpis", tags=["4. Administración y Reportes"])
def obtener_kpis_gerencia():
    sin_facturar = [r for r in repo.registros_facturables.values() if not r["folio_factura"]]
    return {
        "total_cotizaciones": len(repo.cotizaciones),
        "total_ordenes": len(repo.ordenes),
        "servicios_pendientes_facturar": len(sin_facturar),
        "cambios_personal_registrados": len(repo.cambios_personal),
    }