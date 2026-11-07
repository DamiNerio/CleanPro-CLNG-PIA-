"""Mappers: convierten los agregados del dominio a diccionarios serializables (JSON) y de regreso.

Mantienen al dominio libre de detalles de base de datos: las entidades no saben
cómo se guardan (persistence ignorance).
"""
from datetime import datetime
from typing import Any, Dict, Optional

from src.domain.entities import (
    Cliente,
    CotizacionFormal,
    Cuadrilla,
    Incidencia,
    OrdenDeServicio,
    ServicioExtra,
)
from src.domain.state_machines import EstadoCotizacion, EstadoOrdenServicio
from src.domain.value_objects import Descuento, FirmaConformidad, Monto, Superficie


def _iso(fecha: Optional[datetime]) -> Optional[str]:
    return fecha.isoformat() if fecha else None


def _fecha(valor: Optional[str]) -> Optional[datetime]:
    return datetime.fromisoformat(valor) if valor else None


# ---------------------------------------------------------------- Cliente
def cliente_a_dict(c: Cliente) -> Dict[str, Any]:
    return {"nombre": c.nombre, "contacto": c.contacto, "fecha_registro": _iso(c.fecha_registro)}


def dict_a_cliente(d: Dict[str, Any]) -> Cliente:
    return Cliente(nombre=d["nombre"], contacto=d["contacto"], fecha_registro=_fecha(d["fecha_registro"]))


# ---------------------------------------------------------------- Cuadrilla
def cuadrilla_a_dict(c: Cuadrilla) -> Dict[str, Any]:
    return {
        "id": c.id,
        "integrantes": list(c.integrantes),
        "estado": c.estado,
        "ventanas_asignadas": [[_iso(i), _iso(f)] for i, f in c.ventanas_asignadas],
    }


def dict_a_cuadrilla(d: Dict[str, Any]) -> Cuadrilla:
    return Cuadrilla(
        id=d["id"],
        integrantes=list(d["integrantes"]),
        estado=d["estado"],
        ventanas_asignadas=[(_fecha(i), _fecha(f)) for i, f in d["ventanas_asignadas"]],
    )


# ---------------------------------------------------------------- Cotización
def cotizacion_a_dict(c: CotizacionFormal) -> Dict[str, Any]:
    return {
        "folio": c.folio,
        "cliente_nombre": c.cliente_nombre,
        "datos_contacto": c.datos_contacto,
        "ubicacion": c.ubicacion,
        "tipo_inmueble": c.tipo_inmueble,
        "superficie_m2": c.superficie.metros_cuadrados,
        "frecuencia": c.frecuencia,
        "extras_solicitados": c.extras_solicitados,
        "canal_origen": c.canal_origen,
        "estado": c.estado.value,
        "descuento": {"porcentaje": c.descuento.porcentaje, "motivo": c.descuento.motivo, "usuario": c.descuento.usuario},
        "subtotal": c.subtotal.valor,
        "total": c.total.valor,
        "horas_persona_sugeridas": c.horas_persona_sugeridas,
        "personal_sugerido": c.personal_sugerido,
        "autorizado_por_gerencia": c.autorizado_por_gerencia,
        "fecha_creacion": _iso(c.fecha_creacion),
        "fecha_respuesta": _iso(c.fecha_respuesta),
    }


def dict_a_cotizacion(d: Dict[str, Any]) -> CotizacionFormal:
    c = CotizacionFormal(
        folio=d["folio"],
        cliente_nombre=d["cliente_nombre"],
        datos_contacto=d["datos_contacto"],
        ubicacion=d["ubicacion"],
        tipo_inmueble=d["tipo_inmueble"],
        superficie=Superficie(d["superficie_m2"]),
        frecuencia=d["frecuencia"],
        extras_solicitados=d["extras_solicitados"],
        canal_origen=d["canal_origen"],
        descuento=Descuento(**d["descuento"]),
        autorizado_por_gerencia=d["autorizado_por_gerencia"],
        fecha_creacion=_fecha(d["fecha_creacion"]),
        fecha_respuesta=_fecha(d["fecha_respuesta"]),
    )
    # Se restauran los valores guardados tal cual (no se recalculan con la configuración actual).
    c.estado = EstadoCotizacion(d["estado"])
    c.subtotal = Monto(d["subtotal"])
    c.total = Monto(d["total"])
    c.horas_persona_sugeridas = d["horas_persona_sugeridas"]
    c.personal_sugerido = d["personal_sugerido"]
    return c


# ---------------------------------------------------------------- Orden de servicio
def orden_a_dict(o: OrdenDeServicio) -> Dict[str, Any]:
    return {
        "folio": o.folio,
        "folio_cotizacion": o.folio_cotizacion,
        "cliente_nombre": o.cliente_nombre,
        "datos_contacto": o.datos_contacto,
        "ubicacion": o.ubicacion,
        "superficie_m2": o.superficie.metros_cuadrados,
        "precio_total": o.precio_total.valor,
        "duracion_estimada_horas": o.duracion_estimada_horas,
        "estado": o.estado.value,
        "fecha_inicio_programada": _iso(o.fecha_inicio_programada),
        "fecha_fin_programada": _iso(o.fecha_fin_programada),
        "cuadrilla_id": o.cuadrilla_asignada.id if o.cuadrilla_asignada else None,
        "hora_inicio_real": _iso(o.hora_inicio_real),
        "hora_fin_real": _iso(o.hora_fin_real),
        "incidencias": [
            {"tipo": i.tipo, "descripcion": i.descripcion, "fotos": list(i.fotos), "fecha_hora": _iso(i.fecha_hora)}
            for i in o.incidencias
        ],
        "extras": [
            {
                "descripcion": e.descripcion,
                "costo": e.costo.valor,
                "autorizado_por_cliente": e.autorizado_por_cliente,
                "fecha_autorizacion": _iso(e.fecha_autorizacion),
            }
            for e in o.extras
        ],
        "firma": (
            {
                "nombre_firmante": o.firma.nombre_firmante,
                "conformidad": o.firma.conformidad,
                "motivo_inconformidad": o.firma.motivo_inconformidad,
                "fecha_hora": _iso(o.firma.fecha_hora),
            }
            if o.firma
            else None
        ),
        "monto_facturable": o.monto_facturable.valor if o.monto_facturable else None,
        "folio_factura": o.folio_factura,
    }


def dict_a_orden(d: Dict[str, Any], cuadrilla: Optional[Cuadrilla]) -> OrdenDeServicio:
    firma = d.get("firma")
    return OrdenDeServicio(
        folio=d["folio"],
        folio_cotizacion=d["folio_cotizacion"],
        cliente_nombre=d["cliente_nombre"],
        datos_contacto=d.get("datos_contacto", ""),
        ubicacion=d["ubicacion"],
        superficie=Superficie(d["superficie_m2"]),
        precio_total=Monto(d["precio_total"]),
        duracion_estimada_horas=d["duracion_estimada_horas"],
        estado=EstadoOrdenServicio(d["estado"]),
        fecha_inicio_programada=_fecha(d["fecha_inicio_programada"]),
        fecha_fin_programada=_fecha(d["fecha_fin_programada"]),
        cuadrilla_asignada=cuadrilla,
        hora_inicio_real=_fecha(d["hora_inicio_real"]),
        hora_fin_real=_fecha(d["hora_fin_real"]),
        incidencias=[
            Incidencia(tipo=i["tipo"], descripcion=i["descripcion"], fotos=list(i["fotos"]), fecha_hora=_fecha(i["fecha_hora"]))
            for i in d["incidencias"]
        ],
        extras=[
            ServicioExtra(
                descripcion=e["descripcion"],
                costo=Monto(e["costo"]),
                autorizado_por_cliente=e["autorizado_por_cliente"],
                fecha_autorizacion=_fecha(e["fecha_autorizacion"]),
            )
            for e in d["extras"]
        ],
        firma=(
            FirmaConformidad(
                nombre_firmante=firma["nombre_firmante"],
                conformidad=firma["conformidad"],
                motivo_inconformidad=firma["motivo_inconformidad"],
                fecha_hora=_fecha(firma["fecha_hora"]),
            )
            if firma
            else None
        ),
        monto_facturable=Monto(d["monto_facturable"]) if d["monto_facturable"] is not None else None,
        folio_factura=d.get("folio_factura"),
    )
