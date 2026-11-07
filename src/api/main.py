"""Capa API (controladores delgados) de CleanPro.

Los endpoints solo traducen HTTP <-> casos de uso. Las reglas de negocio viven
en el dominio y los errores se traducen a códigos HTTP en un solo lugar
(manejadores de excepciones al final del archivo).
"""
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Optional

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from src.application.services import (
    RecursoNoEncontrado,
    ServicioAdministracion,
    ServicioCotizacion,
    ServicioEjecucion,
    ServicioExcepciones,
    ServicioProgramacion,
)
from src.domain.entities import CotizacionFormal, OrdenDeServicio
from src.domain.exceptions import AutorizacionRequerida, ConflictoDeAgenda, DomainError, TransicionInvalida
from src.infrastructure.config import settings
from src.infrastructure.repositories import crear_repositorio

app = FastAPI(
    title="CleanPro - API de Lógica de Negocios (PIA CLNG)",
    description=(
        "Implementación DDD + Specification + State Machine para el Caso 12 CleanPro (Equipo 12 - FIME UANL).\n\n"
        "* **Portal del cliente:** `/`\n* **Intranet del personal:** `/admin`\n\n"
        "Códigos de error: 404 recurso inexistente · 403 requiere autorización de gerencia · "
        "409 transición de estado inválida o traslape de agenda · 422 dato o regla de negocio inválida."
    ),
    version="2.0.0",
)

# Composición de dependencias: el repositorio concreto se elige por DATABASE_URL (12-Factor).
repo = crear_repositorio(settings.DATABASE_URL)
srv_cotizacion = ServicioCotizacion(repo)
srv_programacion = ServicioProgramacion(repo)
srv_ejecucion = ServicioEjecucion(repo)
srv_excepciones = ServicioExcepciones(repo)
srv_administracion = ServicioAdministracion(repo)

ZONA_LOCAL = timezone(timedelta(hours=settings.ZONA_HORARIA_OFFSET_HORAS))


def ahora_local() -> datetime:
    """Hora actual de Monterrey sin zona (igual que las fechas capturadas en los formularios)."""
    return datetime.now(ZONA_LOCAL).replace(tzinfo=None)


def parsear_fecha(valor: str) -> datetime:
    try:
        fecha = datetime.fromisoformat(valor)
    except ValueError:
        raise DomainError(f"Fecha inválida: '{valor}'. Use el formato AAAA-MM-DDTHH:MM:SS.")
    if fecha.tzinfo is not None:
        fecha = fecha.astimezone(ZONA_LOCAL).replace(tzinfo=None)
    return fecha


# ------------------------------------------------------------------ DTOs
class SolicitudCotizacionDTO(BaseModel):
    cliente_nombre: str = Field(..., examples=["Empresa Alfa S.A."])
    datos_contacto: str = Field(..., examples=["contacto@alfa.com"])
    ubicacion: str = Field(..., examples=["Av. Universidad, San Nicolás"])
    tipo_inmueble: str = Field(..., examples=["oficina"])
    superficie_m2: float = Field(..., examples=[240.0])
    frecuencia: str = Field(..., examples=["quincenal"])
    extras: List[Dict[str, float]] = Field(default_factory=list, examples=[[{"horas": 1.0, "costo": 450.0}]])
    canal_origen: str = Field(default="web")


class DescuentoDTO(BaseModel):
    porcentaje: float = Field(..., examples=[8.0])
    rol: str = Field(..., examples=["coordinador"])
    usuario: str = Field(..., examples=["coord_camila"])
    motivo: str = Field(default="Contrato de frecuencia")


class ProgramacionDTO(BaseModel):
    fecha_inicio_iso: str = Field(..., examples=["2026-11-20T09:00:00"])
    id_cuadrilla: str = Field(..., examples=["C-05"])


class IncidenciaDTO(BaseModel):
    tipo: str = Field(..., examples=["daño en mobiliario"])
    descripcion: str = Field(..., examples=["Persiana dañada en sala de juntas"])
    fotos: List[str] = Field(..., examples=[["https://cleanpro.mx/evidencias/foto1.jpg"]])


class CierreDTO(BaseModel):
    nombre_firmante: str = Field(..., examples=["Ing. Roberto Garza"])
    conformidad: bool = Field(default=True)
    motivo_inconformidad: str = Field(default="")


class AusenciaDTO(BaseModel):
    integrante_ausente: str = Field(..., examples=["J. Ramírez"])
    integrante_reemplazo: Optional[str] = Field(default=None, examples=["D. Nerio"])
    motivo: str = Field(..., examples=["Incapacidad"])


class AccesoDenegadoDTO(BaseModel):
    evidencia: str = Field(default="evidencia_acceso_denegado.jpg", examples=["foto_puerta_cerrada.jpg"])


class CancelacionDTO(BaseModel):
    fecha_solicitud_iso: Optional[str] = Field(default=None, description="Si se omite, se usa la hora actual de Monterrey.")
    fuerza_mayor: bool = Field(default=False, description="Causa de fuerza mayor evaluada por el coordinador (sin cargo).")


class ReprogramacionDTO(BaseModel):
    nueva_fecha_iso: str = Field(..., examples=["2026-11-25T09:00:00"])
    fecha_solicitud_iso: Optional[str] = Field(default=None)


class ServicioExtraDTO(BaseModel):
    descripcion: str = Field(..., examples=["Limpieza de terraza"])
    costo: float = Field(..., examples=[600.0])
    autorizado_por_cliente: bool = Field(..., examples=[True])


class AjusteSuperficieDTO(BaseModel):
    nueva_superficie_m2: float = Field(..., examples=[200.0])
    fotos: List[str] = Field(..., examples=[["evidencia_m2.jpg"]])
    autorizado_por_cliente: bool = Field(..., examples=[True])


class AutorizacionGerenciaDTO(BaseModel):
    usuario_gerencia: str = Field(default="Lic. Renata Cárdenas")


class FacturaDTO(BaseModel):
    folio_factura: str = Field(..., examples=["FAC-2026-0001"])


# ------------------------------------------------------------------ Presentación
def cotizacion_json(c: CotizacionFormal) -> Dict:
    return {
        "folio": c.folio,
        "cliente": c.cliente_nombre,
        "superficie_m2": c.superficie.metros_cuadrados,
        "tipo_inmueble": c.tipo_inmueble,
        "frecuencia": c.frecuencia,
        "descuento": c.descuento.porcentaje,
        "subtotal": c.subtotal.valor,
        "total": c.total.valor,
        "estado": c.estado.value,
        "horas_sugeridas": c.horas_persona_sugeridas,
        "personal_sugerido": c.personal_sugerido,
        "autorizado_por": c.autorizado_por_gerencia,
    }


def orden_json(o: OrdenDeServicio) -> Dict:
    return {
        "folio": o.folio,
        "folio_cotizacion": o.folio_cotizacion,
        "cliente": o.cliente_nombre,
        "ubicacion": o.ubicacion,
        "superficie_m2": o.superficie.metros_cuadrados,
        "precio_total": o.precio_total.valor,
        "estado": o.estado.value,
        "fecha_programada": o.fecha_inicio_programada.isoformat() if o.fecha_inicio_programada else None,
        "cuadrilla": o.cuadrilla_asignada.id if o.cuadrilla_asignada else None,
        "integrantes": list(o.cuadrilla_asignada.integrantes) if o.cuadrilla_asignada else [],
        "incidencias": len(o.incidencias),
        "extras": [
            {"descripcion": e.descripcion, "costo": e.costo.valor, "autorizado": e.autorizado_por_cliente}
            for e in o.extras
        ],
        "monto_facturable": o.monto_facturable.valor if o.monto_facturable else None,
        "folio_factura": o.folio_factura,
    }


# ------------------------------------------------------------------ Vistas web
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def portal_cliente():
    return HTMLResponse((Path(__file__).parent / "index.html").read_text(encoding="utf-8"))


@app.get("/admin", response_class=HTMLResponse, include_in_schema=False)
def intranet_administrativa():
    return HTMLResponse((Path(__file__).parent / "admin.html").read_text(encoding="utf-8"))


@app.get("/health", tags=["0. Sistema"])
def health():
    return {"status": "ok", "persistencia": type(repo).__name__}


# ------------------------------------------------------------------ 1. Cotización
@app.post("/api/cotizaciones", tags=["1. Cotización"], summary="US-01/US-02: solicitar cotización")
def crear_cotizacion(dto: SolicitudCotizacionDTO):
    cot = srv_cotizacion.solicitar_cotizacion(dto.model_dump())
    return {
        "folio": cot.folio,
        "estado": cot.estado.value,
        "subtotal": cot.subtotal.valor,
        "total": cot.total.valor,
        "horas_persona_sugeridas": cot.horas_persona_sugeridas,
        "personal_sugerido": cot.personal_sugerido,
    }


@app.get("/api/cotizaciones/{folio}", tags=["1. Cotización"], summary="Consultar una cotización")
def obtener_cotizacion(folio: str):
    return cotizacion_json(srv_cotizacion.consultar_cotizacion(folio))


@app.patch("/api/cotizaciones/{folio}/descuento", tags=["1. Cotización"], summary="US-03: descuento (RN-01)")
def aplicar_descuento(folio: str, dto: DescuentoDTO):
    cot = srv_cotizacion.aplicar_descuento(folio, dto.porcentaje, dto.rol, dto.usuario, dto.motivo)
    return {"folio": cot.folio, "estado": cot.estado.value, "total": cot.total.valor}


@app.post("/api/cotizaciones/{folio}/autorizar", tags=["1. Cotización"], summary="US-04: gerencia autoriza excepción")
def autorizar_gerencia(folio: str, dto: Optional[AutorizacionGerenciaDTO] = None):
    usuario = (dto or AutorizacionGerenciaDTO()).usuario_gerencia
    cot = srv_cotizacion.autorizar_cotizacion(folio, usuario)
    return {"folio": cot.folio, "estado": cot.estado.value, "autorizado_por": cot.autorizado_por_gerencia}


@app.post("/api/cotizaciones/{folio}/descartar", tags=["1. Cotización"], summary="US-04: gerencia descarta la propuesta")
def descartar_gerencia(folio: str, dto: Optional[AutorizacionGerenciaDTO] = None):
    usuario = (dto or AutorizacionGerenciaDTO()).usuario_gerencia
    cot = srv_cotizacion.descartar_cotizacion(folio, usuario)
    return {"folio": cot.folio, "estado": cot.estado.value}


@app.post("/api/cotizaciones/{folio}/aceptar", tags=["1. Cotización"], summary="US-05: cliente acepta")
def aceptar_cotizacion(folio: str):
    orden = srv_cotizacion.aceptar_cotizacion(folio)
    return {"folio_cotizacion": folio, "folio_orden": orden.folio, "estado_orden": orden.estado.value}


@app.post("/api/cotizaciones/{folio}/rechazar", tags=["1. Cotización"], summary="US-05: cliente rechaza")
def rechazar_cotizacion(folio: str):
    cot = srv_cotizacion.rechazar_cotizacion(folio)
    return {"folio": cot.folio, "estado": cot.estado.value}


# ------------------------------------------------------------------ 2. Programación
@app.post("/api/ordenes/{folio_orden}/programar", tags=["2. Programación y Asignación"], summary="US-06/US-07: programar y asignar cuadrilla")
def programar_orden(folio_orden: str, dto: ProgramacionDTO):
    orden = srv_programacion.programar_y_asignar(folio_orden, parsear_fecha(dto.fecha_inicio_iso), dto.id_cuadrilla)
    return {
        "folio_orden": orden.folio,
        "estado": orden.estado.value,
        "cuadrilla": orden.cuadrilla_asignada.id,
        "integrantes": orden.cuadrilla_asignada.integrantes,
        "inicio": orden.fecha_inicio_programada.isoformat(),
        "fin_estimado": orden.fecha_fin_programada.isoformat(),
    }


@app.get("/api/agenda", tags=["2. Programación y Asignación"], summary="US-08: agenda del día del supervisor")
def agenda_del_dia(fecha: Optional[date] = None):
    dia = fecha or ahora_local().date()
    return {"fecha": dia.isoformat(), "servicios": [orden_json(o) for o in srv_programacion.agenda_del_dia(dia)]}


@app.get("/api/cuadrillas", tags=["2. Programación y Asignación"], summary="Cuadrillas y su agenda")
def listar_cuadrillas():
    return [
        {
            "id": c.id,
            "integrantes": c.integrantes,
            "estado": c.estado,
            "ventanas": [[i.isoformat(), f.isoformat()] for i, f in c.ventanas_asignadas],
        }
        for c in srv_programacion.listar_cuadrillas()
    ]


# ------------------------------------------------------------------ 3. Ejecución
@app.get("/api/ordenes/{folio_orden}", tags=["3. Ejecución"], summary="Consultar una orden de servicio")
def obtener_orden(folio_orden: str):
    return orden_json(srv_ejecucion.consultar_orden(folio_orden))


@app.post("/api/ordenes/{folio_orden}/iniciar", tags=["3. Ejecución"], summary="US-09: registrar inicio")
def iniciar_servicio(folio_orden: str):
    orden = srv_ejecucion.registrar_inicio(folio_orden, ahora_local())
    return {"folio_orden": orden.folio, "estado": orden.estado.value, "hora_inicio": orden.hora_inicio_real}


@app.post("/api/ordenes/{folio_orden}/incidencias", tags=["3. Ejecución"], summary="US-10: incidencia con evidencia")
def registrar_incidencia(folio_orden: str, dto: IncidenciaDTO):
    orden = srv_ejecucion.documentar_incidencia(folio_orden, dto.tipo, dto.descripcion, dto.fotos)
    return {"folio_orden": orden.folio, "total_incidencias": len(orden.incidencias)}


@app.post("/api/ordenes/{folio_orden}/cerrar", tags=["3. Ejecución"], summary="US-11: cierre con firma del cliente")
def cerrar_servicio(folio_orden: str, dto: CierreDTO):
    orden = srv_ejecucion.cerrar_servicio(folio_orden, dto.nombre_firmante, dto.conformidad, dto.motivo_inconformidad)
    return {"folio_orden": orden.folio, "estado": orden.estado.value, "monto_facturable": orden.monto_facturable.valor}


# ------------------------------------------------------------------ 4. Excepciones operativas
@app.post("/api/ordenes/{folio_orden}/ausencia", tags=["4. Excepciones Operativas"], summary="US-12/US-17: ausencia de personal")
def reportar_ausencia(folio_orden: str, dto: AusenciaDTO):
    return srv_excepciones.reportar_ausencia(folio_orden, dto.integrante_ausente, dto.motivo, dto.integrante_reemplazo)


@app.post("/api/ordenes/{folio_orden}/acceso-denegado", tags=["4. Excepciones Operativas"], summary="US-13: acceso denegado (RN-05, 100%)")
def acceso_denegado(folio_orden: str, dto: Optional[AccesoDenegadoDTO] = None):
    evidencia = (dto or AccesoDenegadoDTO()).evidencia
    orden = srv_excepciones.registrar_acceso_denegado(folio_orden, evidencia)
    return {"folio_orden": orden.folio, "estado": orden.estado.value, "cargo": orden.monto_facturable.valor}


@app.post("/api/ordenes/{folio_orden}/extras", tags=["4. Excepciones Operativas"], summary="US-14: servicio adicional en sitio (RN-06)")
def servicio_extra(folio_orden: str, dto: ServicioExtraDTO):
    orden = srv_excepciones.autorizar_servicio_extra(folio_orden, dto.descripcion, dto.costo, dto.autorizado_por_cliente)
    return {"folio_orden": orden.folio, "precio_total": orden.precio_total.valor, "extras": orden_json(orden)["extras"]}


@app.post("/api/ordenes/{folio_orden}/ajuste-superficie", tags=["4. Excepciones Operativas"], summary="US-15: inmueble mayor a lo reportado (RN-07)")
def ajuste_superficie(folio_orden: str, dto: AjusteSuperficieDTO):
    orden = srv_excepciones.ajustar_superficie(folio_orden, dto.nueva_superficie_m2, dto.fotos, dto.autorizado_por_cliente)
    return {"folio_orden": orden.folio, "superficie_m2": orden.superficie.metros_cuadrados, "precio_total": orden.precio_total.valor}


@app.post("/api/ordenes/{folio_orden}/cancelar", tags=["4. Excepciones Operativas"], summary="US-16: cancelación (RN-04)")
def cancelar_orden(folio_orden: str, dto: Optional[CancelacionDTO] = None):
    dto = dto or CancelacionDTO()
    fecha = parsear_fecha(dto.fecha_solicitud_iso) if dto.fecha_solicitud_iso else ahora_local()
    return srv_excepciones.cancelar_o_reprogramar(folio_orden, fecha_solicitud=fecha, fuerza_mayor=dto.fuerza_mayor)


@app.post("/api/ordenes/{folio_orden}/reprogramar", tags=["4. Excepciones Operativas"], summary="US-16: reprogramación (RN-08)")
def reprogramar_orden(folio_orden: str, dto: ReprogramacionDTO):
    fecha = parsear_fecha(dto.fecha_solicitud_iso) if dto.fecha_solicitud_iso else ahora_local()
    return srv_excepciones.cancelar_o_reprogramar(folio_orden, fecha_solicitud=fecha, nueva_fecha=parsear_fecha(dto.nueva_fecha_iso))


# ------------------------------------------------------------------ 5. Administración
@app.post("/api/facturables/{folio_orden}/facturar", tags=["5. Administración y Reportes"], summary="US-18: vincular factura (RN-09)")
def facturar(folio_orden: str, dto: FacturaDTO):
    return srv_administracion.facturar(folio_orden, dto.folio_factura)


@app.get("/api/administracion/kpis", tags=["5. Administración y Reportes"], summary="US-19: indicadores de gerencia")
def obtener_kpis():
    return srv_administracion.kpis()


@app.get("/api/estado", tags=["5. Administración y Reportes"], summary="Tablero completo de la intranet")
def obtener_estado_completo():
    return {
        "kpis": srv_administracion.kpis(),
        "cotizaciones": [cotizacion_json(c) for c in repo.listar_cotizaciones()],
        "ordenes": [orden_json(o) for o in repo.listar_ordenes()],
        "facturables": repo.listar_registros_facturables(),
        "cambios_personal": repo.listar_cambios_personal(),
    }


@app.get("/api/clientes/solicitudes", tags=["6. Portal del Cliente"], summary="Cotizaciones y servicios de un cliente")
def solicitudes_de_cliente(contacto: str):
    datos = srv_administracion.solicitudes_de_cliente(contacto)
    return {
        "cotizaciones": [cotizacion_json(c) for c in datos["cotizaciones"]],
        "ordenes": [orden_json(o) for o in datos["ordenes"]],
    }


# ------------------------------------------------------------------ Traducción de errores
def _error(status: int, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=status, content={"detail": str(exc), "tipo": type(exc).__name__})


@app.exception_handler(RecursoNoEncontrado)
def manejar_no_encontrado(request: Request, exc: RecursoNoEncontrado):
    return _error(404, exc)


@app.exception_handler(DomainError)
def manejar_error_dominio(request: Request, exc: DomainError):
    if isinstance(exc, AutorizacionRequerida):
        return _error(403, exc)
    if isinstance(exc, (TransicionInvalida, ConflictoDeAgenda)):
        return _error(409, exc)
    return _error(422, exc)
