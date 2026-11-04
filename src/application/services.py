from datetime import datetime
from typing import Dict, List, Optional
from src.domain.entities import CotizacionFormal, OrdenDeServicio, Cuadrilla
from src.domain.value_objects import Superficie, FirmaConformidad, DomainError
from src.domain.specifications import ClienteSuperaLimiteReprogramacionesSpec
from src.domain.state_machines import EstadoOrdenServicio, OrdenServicioStateMachine

class CleanProRepository:
    """Repositorio central para persistencia de Agregados y Registros de Administración."""
    def __init__(self):
        self.cotizaciones: Dict[str, CotizacionFormal] = {}
        self.ordenes: Dict[str, OrdenDeServicio] = {}
        self.cuadrillas: Dict[str, Cuadrilla] = {
            "C-03": Cuadrilla(id="C-03", integrantes=["J. Ramírez", "M. López"]),
            "C-05": Cuadrilla(id="C-05", integrantes=["A. Garza", "P. Sánchez"]),
            "C-07": Cuadrilla(id="C-07", integrantes=["R. Treviño", "L. Morales"]),
        }
        self.cambios_personal: List[Dict] = []
        self.registros_facturables: Dict[str, Dict] = {}
        self.reprogramaciones_por_cliente: Dict[str, int] = {}

class ServicioCotizacion:
    def __init__(self, repo: CleanProRepository):
        self.repo = repo

    def solicitar_cotizacion(self, datos: Dict) -> CotizacionFormal:
        folio = datos.get("folio") or f"COT-{1000 + len(self.repo.cotizaciones) + 1}"
        cot = CotizacionFormal(
            folio=folio,
            cliente_nombre=datos["cliente_nombre"],
            datos_contacto=datos["datos_contacto"],
            ubicacion=datos["ubicacion"],
            tipo_inmueble=datos["tipo_inmueble"],
            superficie=Superficie(float(datos["superficie_m2"])),
            frecuencia=datos["frecuencia"],
            extras_solicitados=datos.get("extras", []),
            canal_origen=datos.get("canal_origen", "web"),
        )
        self.repo.cotizaciones[folio] = cot
        return cot

    def aplicar_descuento(self, folio: str, porcentaje: float, rol: str, usuario: str, motivo: str = "Contrato frecuencia") -> CotizacionFormal:
        cot = self.repo.cotizaciones[folio]
        cot.aplicar_descuento(porcentaje=porcentaje, rol=rol, usuario=usuario, motivo=motivo)
        return cot

    def autorizar_cotizacion(self, folio: str, usuario_gerencia: str) -> CotizacionFormal:
        cot = self.repo.cotizaciones[folio]
        cot.autorizar_por_gerencia(usuario_gerencia)
        return cot

    def aceptar_cotizacion(self, folio: str) -> OrdenDeServicio:
        cot = self.repo.cotizaciones[folio]
        orden = cot.aceptar_por_cliente()
        self.repo.ordenes[orden.folio] = orden
        return orden

class ServicioProgramacion:
    def __init__(self, repo: CleanProRepository):
        self.repo = repo

    def programar_y_asignar(self, folio_orden: str, fecha_inicio: datetime, id_cuadrilla: str) -> OrdenDeServicio:
        orden = self.repo.ordenes[folio_orden]
        cuadrilla = self.repo.cuadrillas[id_cuadrilla]
        orden.programar(fecha_inicio=fecha_inicio, cuadrilla=cuadrilla)
        return orden

class ServicioEjecucion:
    def __init__(self, repo: CleanProRepository):
        self.repo = repo

    def registrar_inicio(self, folio_orden: str, hora_inicio: Optional[datetime] = None) -> OrdenDeServicio:
        orden = self.repo.ordenes[folio_orden]
        orden.registrar_inicio(hora_inicio)
        return orden

    def documentar_incidencia(self, folio_orden: str, tipo: str, descripcion: str, fotos: List[str]) -> OrdenDeServicio:
        orden = self.repo.ordenes[folio_orden]
        orden.documentar_incidencia(tipo=tipo, descripcion=descripcion, fotos=fotos)
        return orden

    def cerrar_servicio(self, folio_orden: str, nombre_firmante: str, conformidad: bool, motivo_inconformidad: str = "") -> OrdenDeServicio:
        orden = self.repo.ordenes[folio_orden]
        firma = FirmaConformidad(
            nombre_firmante=nombre_firmante,
            conformidad=conformidad,
            motivo_inconformidad=motivo_inconformidad,
        )
        orden.cerrar_servicio(firma)
        # RN-09 y US-18: Generar registro facturable automático
        self.repo.registros_facturables[orden.folio] = {
            "folio_orden": orden.folio,
            "cliente": orden.cliente_nombre,
            "monto": orden.monto_facturable.valor,
            "motivo": "Servicio ejecutado",
            "folio_factura": None,
        }
        return orden

class ServicioExcepciones:
    def __init__(self, repo: CleanProRepository):
        self.repo = repo

    def reportar_ausencia(self, folio_orden: str, integrante_ausente: str, motivo: str, integrante_reemplazo: Optional[str] = None) -> Dict:
        orden = self.repo.ordenes[folio_orden]
        if orden.cuadrilla_asignada and integrante_ausente in orden.cuadrilla_asignada.integrantes:
            orden.cuadrilla_asignada.integrantes.remove(integrante_ausente)
            if integrante_reemplazo:
                orden.cuadrilla_asignada.integrantes.append(integrante_reemplazo)
        registro = {
            "id": f"NOM-{len(self.repo.cambios_personal) + 1}",
            "folio_orden": folio_orden,
            "integrante_saliente": integrante_ausente,
            "integrante_entrante": integrante_reemplazo or "Equipo reducido",
            "motivo": motivo,
            "fecha": datetime.utcnow().isoformat(),
            "procesado_en_nomina": False,
        }
        self.repo.cambios_personal.append(registro)
        return registro

    def registrar_acceso_denegado(self, folio_orden: str, evidencia_foto: str) -> OrdenDeServicio:
        orden = self.repo.ordenes[folio_orden]
        orden.registrar_acceso_denegado(evidencia_foto)
        self.repo.registros_facturables[orden.folio] = {
            "folio_orden": orden.folio,
            "cliente": orden.cliente_nombre,
            "monto": orden.monto_facturable.valor,
            "motivo": "Penalización 100% por acceso denegado (RN-05)",
            "folio_factura": None,
        }
        return orden

    def cancelar_o_reprogramar(self, folio_orden: str, fecha_solicitud: datetime, nueva_fecha: Optional[datetime] = None, fuerza_mayor: bool = False) -> Dict:
        orden = self.repo.ordenes[folio_orden]
        alerta_gerencia = False
        if nueva_fecha:
            conteo = self.repo.reprogramaciones_por_cliente.get(orden.cliente_nombre, 0) + 1
            self.repo.reprogramaciones_por_cliente[orden.cliente_nombre] = conteo
            alerta_gerencia = ClienteSuperaLimiteReprogramacionesSpec().is_satisfied_by(conteo)
            if orden.cuadrilla_asignada and orden.fecha_inicio_programada and orden.fecha_fin_programada:
                orden.cuadrilla_asignada.liberar_horario(orden.fecha_inicio_programada, orden.fecha_fin_programada)
            orden.programar(nueva_fecha, orden.cuadrilla_asignada)
            return {"estado": orden.estado.value, "reprogramaciones_mes": conteo, "alerta_gerencia_rn08": alerta_gerencia}

        orden.cancelar(fecha_solicitud=fecha_solicitud, fuerza_mayor=fuerza_mayor)
        if orden.estado == EstadoOrdenServicio.CANCELADA_CON_CARGO:
            self.repo.registros_facturables[orden.folio] = {
                "folio_orden": orden.folio,
                "cliente": orden.cliente_nombre,
                "monto": orden.monto_facturable.valor,
                "motivo": "Penalización 50% por cancelación tardía <24h (RN-04)",
                "folio_factura": None,
            }
        return {"estado": orden.estado.value, "cargo": orden.monto_facturable.valor if orden.monto_facturable else 0.0}