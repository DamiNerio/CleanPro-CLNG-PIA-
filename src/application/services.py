"""Capa de aplicación (Service Layer): orquesta los casos de uso.

Los servicios no contienen reglas de negocio: recuperan el agregado del
repositorio, le piden que ejecute la operación (las reglas viven en el dominio)
y guardan el resultado. Dependen del puerto RepositorioCleanPro, no de una base
de datos concreta (DIP).
"""
from datetime import date, datetime
from typing import Dict, List, Optional

from src.domain.entities import Cliente, CotizacionFormal, Cuadrilla, OrdenDeServicio
from src.domain.repositories import RepositorioCleanPro
from src.domain.specifications import ClienteSuperaLimiteReprogramacionesSpec
from src.domain.state_machines import EstadoCotizacion, EstadoOrdenServicio
from src.domain.value_objects import FirmaConformidad, Superficie


class RecursoNoEncontrado(LookupError):
    """El folio o identificador solicitado no existe (la API lo traduce a HTTP 404)."""


class _ServicioBase:
    def __init__(self, repo: RepositorioCleanPro):
        self.repo = repo

    def _cotizacion(self, folio: str) -> CotizacionFormal:
        cot = self.repo.obtener_cotizacion(folio)
        if cot is None:
            raise RecursoNoEncontrado(f"Cotización {folio} no encontrada.")
        return cot

    def _orden(self, folio: str) -> OrdenDeServicio:
        orden = self.repo.obtener_orden(folio)
        if orden is None:
            raise RecursoNoEncontrado(f"Orden de servicio {folio} no encontrada.")
        return orden

    def _cuadrilla(self, id_cuadrilla: str) -> Cuadrilla:
        cuadrilla = self.repo.obtener_cuadrilla(id_cuadrilla)
        if cuadrilla is None:
            raise RecursoNoEncontrado(f"Cuadrilla {id_cuadrilla} no encontrada.")
        return cuadrilla

    def consultar_cotizacion(self, folio: str) -> CotizacionFormal:
        return self._cotizacion(folio)

    def consultar_orden(self, folio: str) -> OrdenDeServicio:
        return self._orden(folio)

    def _guardar_orden(self, orden: OrdenDeServicio) -> None:
        """Guarda la orden y su cuadrilla (la agenda de la cuadrilla cambia al programar/cancelar)."""
        if orden.cuadrilla_asignada:
            self.repo.guardar_cuadrilla(orden.cuadrilla_asignada)
        self.repo.guardar_orden(orden)

    def _registrar_facturable(self, orden: OrdenDeServicio, motivo: str) -> Dict:
        registro = {
            "folio_orden": orden.folio,
            "cliente": orden.cliente_nombre,
            "monto": orden.monto_facturable.valor,
            "motivo": motivo,
            "folio_factura": None,
        }
        self.repo.guardar_registro_facturable(registro)
        return registro


class ServicioCotizacion(_ServicioBase):
    """US-01 a US-05."""

    def solicitar_cotizacion(self, datos: Dict) -> CotizacionFormal:
        cliente = Cliente(nombre=datos["cliente_nombre"], contacto=datos["datos_contacto"])
        if self.repo.obtener_cliente(cliente.id) is None:
            self.repo.guardar_cliente(cliente)
        cot = CotizacionFormal(
            folio=datos.get("folio") or self.repo.siguiente_folio_cotizacion(),
            cliente_nombre=datos["cliente_nombre"],
            datos_contacto=datos["datos_contacto"],
            ubicacion=datos["ubicacion"],
            tipo_inmueble=datos["tipo_inmueble"],
            superficie=Superficie(float(datos["superficie_m2"])),
            frecuencia=datos["frecuencia"],
            extras_solicitados=datos.get("extras", []),
            canal_origen=datos.get("canal_origen", "web"),
        )
        self.repo.guardar_cotizacion(cot)
        return cot

    def aplicar_descuento(self, folio: str, porcentaje: float, rol: str, usuario: str, motivo: str = "Contrato frecuencia") -> CotizacionFormal:
        cot = self._cotizacion(folio)
        try:
            cot.aplicar_descuento(porcentaje=porcentaje, rol=rol, usuario=usuario, motivo=motivo)
        finally:
            # Aunque el descuento quede bloqueado (>10%), el cambio a "Pendiente de autorización" se persiste.
            self.repo.guardar_cotizacion(cot)
        return cot

    def autorizar_cotizacion(self, folio: str, usuario_gerencia: str) -> CotizacionFormal:
        cot = self._cotizacion(folio)
        cot.autorizar_por_gerencia(usuario_gerencia)
        self.repo.guardar_cotizacion(cot)
        return cot

    def descartar_cotizacion(self, folio: str, usuario_gerencia: str) -> CotizacionFormal:
        cot = self._cotizacion(folio)
        cot.descartar_por_gerencia(usuario_gerencia)
        self.repo.guardar_cotizacion(cot)
        return cot

    def aceptar_cotizacion(self, folio: str) -> OrdenDeServicio:
        cot = self._cotizacion(folio)
        orden = cot.aceptar_por_cliente()
        self.repo.guardar_cotizacion(cot)
        self.repo.guardar_orden(orden)
        return orden

    def rechazar_cotizacion(self, folio: str) -> CotizacionFormal:
        cot = self._cotizacion(folio)
        cot.rechazar_por_cliente()
        self.repo.guardar_cotizacion(cot)
        return cot


class ServicioProgramacion(_ServicioBase):
    """US-06 a US-08."""

    def programar_y_asignar(self, folio_orden: str, fecha_inicio: datetime, id_cuadrilla: str) -> OrdenDeServicio:
        orden = self._orden(folio_orden)
        cuadrilla = self._cuadrilla(id_cuadrilla)
        orden.programar(fecha_inicio=fecha_inicio, cuadrilla=cuadrilla)
        self._guardar_orden(orden)
        return orden

    def agenda_del_dia(self, dia: date) -> List[OrdenDeServicio]:
        ordenes = [
            o for o in self.repo.listar_ordenes()
            if o.fecha_inicio_programada and o.fecha_inicio_programada.date() == dia
        ]
        return sorted(ordenes, key=lambda o: o.fecha_inicio_programada)

    def listar_cuadrillas(self) -> List[Cuadrilla]:
        return self.repo.listar_cuadrillas()


class ServicioEjecucion(_ServicioBase):
    """US-09 a US-11."""

    def registrar_inicio(self, folio_orden: str, hora_inicio: Optional[datetime] = None) -> OrdenDeServicio:
        orden = self._orden(folio_orden)
        orden.registrar_inicio(hora_inicio)
        self._guardar_orden(orden)
        return orden

    def documentar_incidencia(self, folio_orden: str, tipo: str, descripcion: str, fotos: List[str]) -> OrdenDeServicio:
        orden = self._orden(folio_orden)
        orden.documentar_incidencia(tipo=tipo, descripcion=descripcion, fotos=fotos)
        self._guardar_orden(orden)
        return orden

    def cerrar_servicio(self, folio_orden: str, nombre_firmante: str, conformidad: bool, motivo_inconformidad: str = "") -> OrdenDeServicio:
        orden = self._orden(folio_orden)
        firma = FirmaConformidad(
            nombre_firmante=nombre_firmante,
            conformidad=conformidad,
            motivo_inconformidad=motivo_inconformidad,
        )
        orden.cerrar_servicio(firma)
        self._guardar_orden(orden)
        # RN-09 y US-18: todo servicio cerrado genera automáticamente su registro facturable.
        self._registrar_facturable(orden, "Servicio ejecutado")
        return orden


class ServicioExcepciones(_ServicioBase):
    """US-12 a US-17: excepciones operativas."""

    def reportar_ausencia(self, folio_orden: str, integrante_ausente: str, motivo: str, integrante_reemplazo: Optional[str] = None) -> Dict:
        orden = self._orden(folio_orden)
        orden.registrar_ausencia(integrante_ausente, motivo, integrante_reemplazo)
        self._guardar_orden(orden)
        # US-17: el cambio llega a administración sin depender de que alguien avise.
        registro = {
            "id": f"NOM-{len(self.repo.listar_cambios_personal()) + 1}",
            "folio_orden": folio_orden,
            "integrante_saliente": integrante_ausente,
            "integrante_entrante": integrante_reemplazo or "Equipo reducido",
            "motivo": motivo,
            "fecha": datetime.utcnow().isoformat(),
            "procesado_en_nomina": False,
        }
        self.repo.guardar_cambio_personal(registro)
        return registro

    def registrar_acceso_denegado(self, folio_orden: str, evidencia_foto: str) -> OrdenDeServicio:
        orden = self._orden(folio_orden)
        orden.registrar_acceso_denegado(evidencia_foto)
        self._guardar_orden(orden)
        self._registrar_facturable(orden, "Penalización 100% por acceso denegado (RN-05)")
        return orden

    def autorizar_servicio_extra(self, folio_orden: str, descripcion: str, costo: float, autorizado: bool) -> OrdenDeServicio:
        orden = self._orden(folio_orden)
        orden.solicitar_y_autorizar_extra(descripcion, costo, autorizado)
        self._guardar_orden(orden)
        return orden

    def ajustar_superficie(self, folio_orden: str, nueva_superficie_m2: float, fotos: List[str], autorizado_cliente: bool) -> OrdenDeServicio:
        orden = self._orden(folio_orden)
        orden.recalcular_por_superficie_mayor(nueva_superficie_m2, fotos, autorizado_cliente)
        self._guardar_orden(orden)
        return orden

    def cancelar_o_reprogramar(
        self,
        folio_orden: str,
        fecha_solicitud: datetime,
        nueva_fecha: Optional[datetime] = None,
        fuerza_mayor: bool = False,
    ) -> Dict:
        orden = self._orden(folio_orden)
        if nueva_fecha:
            # RN-08: más de 2 reprogramaciones del mismo cliente en un mes -> alerta a gerencia.
            clave = f"{orden.cliente_nombre}|{fecha_solicitud:%Y-%m}"
            conteo = self.repo.incrementar_reprogramaciones(clave)
            alerta_gerencia = ClienteSuperaLimiteReprogramacionesSpec().is_satisfied_by(conteo)
            if orden.cuadrilla_asignada and orden.fecha_inicio_programada and orden.fecha_fin_programada:
                orden.cuadrilla_asignada.liberar_horario(orden.fecha_inicio_programada, orden.fecha_fin_programada)
            orden.programar(nueva_fecha, orden.cuadrilla_asignada)
            self._guardar_orden(orden)
            return {"estado": orden.estado.value, "reprogramaciones_mes": conteo, "alerta_gerencia_rn08": alerta_gerencia}

        orden.cancelar(fecha_solicitud=fecha_solicitud, fuerza_mayor=fuerza_mayor)
        self._guardar_orden(orden)
        if orden.estado == EstadoOrdenServicio.CANCELADA_CON_CARGO:
            self._registrar_facturable(orden, "Penalización 50% por cancelación tardía <24h (RN-04)")
        return {"estado": orden.estado.value, "cargo": orden.monto_facturable.valor if orden.monto_facturable else 0.0}


class ServicioAdministracion(_ServicioBase):
    """US-17 a US-19: facturación, nómina e indicadores."""

    def facturar(self, folio_orden: str, folio_factura: str) -> Dict:
        registro = self.repo.obtener_registro_facturable(folio_orden)
        if registro is None:
            raise RecursoNoEncontrado(f"No hay un registro facturable para la orden {folio_orden}.")
        orden = self._orden(folio_orden)
        orden.facturar(folio_factura)
        self.repo.guardar_orden(orden)
        registro["folio_factura"] = folio_factura
        self.repo.guardar_registro_facturable(registro)
        return registro

    def kpis(self) -> Dict:
        cotizaciones = self.repo.listar_cotizaciones()
        ordenes = self.repo.listar_ordenes()
        facturables = self.repo.listar_registros_facturables()
        aceptadas = sum(1 for c in cotizaciones if c.estado == EstadoCotizacion.ACEPTADA)
        return {
            "total_cotizaciones": len(cotizaciones),
            "cotizaciones_aceptadas": aceptadas,
            "tasa_conversion_pct": round(100.0 * aceptadas / len(cotizaciones), 1) if cotizaciones else 0.0,
            "pendientes_autorizacion": sum(1 for c in cotizaciones if c.estado == EstadoCotizacion.PENDIENTE_AUTORIZACION),
            "total_ordenes": len(ordenes),
            "servicios_con_incidencias": sum(1 for o in ordenes if o.incidencias),
            "servicios_con_inconformidad": sum(1 for o in ordenes if o.estado == EstadoOrdenServicio.CERRADA_INCONFORMIDAD),
            "servicios_pendientes_facturar": sum(1 for r in facturables if not r["folio_factura"]),
            "monto_pendiente_facturar": round(sum(r["monto"] for r in facturables if not r["folio_factura"]), 2),
            "cambios_personal_registrados": len(self.repo.listar_cambios_personal()),
        }

    def solicitudes_de_cliente(self, contacto: str) -> Dict:
        """Portal del cliente: solo sus propias cotizaciones y servicios."""
        cliente_id = Cliente.normalizar_contacto(contacto)
        cotizaciones = [c for c in self.repo.listar_cotizaciones() if Cliente.normalizar_contacto(c.datos_contacto) == cliente_id]
        ordenes = [o for o in self.repo.listar_ordenes() if Cliente.normalizar_contacto(o.datos_contacto) == cliente_id]
        return {"cotizaciones": cotizaciones, "ordenes": ordenes}
