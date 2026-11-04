from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional, Dict
import math

from src.domain.value_objects import Monto, Superficie, Descuento, FirmaConformidad, DomainError
from src.domain.specifications import (
    DescuentoAutorizablePorCoordinadorSpec,
    CotizacionDentroDeLimiteCoordinadorSpec,
    CancelacionSinPenalizacionSpec,
    CuadrillaDisponibleSpec,
)
from src.domain.state_machines import (
    EstadoCotizacion,
    CotizacionStateMachine,
    EstadoOrdenServicio,
    OrdenServicioStateMachine,
)
from src.domain.events import (
    DomainEvent,
    CotizacionAceptada,
    AusenciaReportada,
    AccesoDenegadoRegistrado,
    ServicioCerrado,
)
from src.infrastructure.config import settings

@dataclass
class Incidencia:
    tipo: str
    descripcion: str
    fotos: List[str]
    fecha_hora: datetime = field(default_factory=datetime.utcnow)

    def validar_para_cierre(self):
        if not self.descripcion.strip():
            raise DomainError("El servicio no puede cerrarse con incidencias sin descripción (CA-10.4).")
        if not self.fotos:
            raise DomainError("Toda incidencia requiere al menos una fotografía de evidencia (CA-10.1).")

@dataclass
class ServicioExtra:
    descripcion: str
    costo: Monto
    autorizado_por_cliente: bool = False
    fecha_autorizacion: Optional[datetime] = None

@dataclass
class Cuadrilla:
    id: str
    integrantes: List[str]
    estado: str = "Disponible"
    ventanas_asignadas: List[tuple] = field(default_factory=list)

    def esta_disponible(self, inicio: datetime, fin: datetime) -> bool:
        spec = CuadrillaDisponibleSpec()
        return spec.is_satisfied_by((inicio, fin, self.ventanas_asignadas))

    def asignar_horario(self, inicio: datetime, fin: datetime):
        if not self.esta_disponible(inicio, fin):
            raise DomainError(f"La cuadrilla {self.id} tiene un traslape de horario (CA-06.3, CA-07.2).")
        self.ventanas_asignadas.append((inicio, fin))
        self.estado = "Asignada"

    def liberar_horario(self, inicio: datetime, fin: datetime):
        self.ventanas_asignadas = [v for v in self.ventanas_asignadas if v != (inicio, fin)]
        if not self.ventanas_asignadas:
            self.estado = "Disponible"

@dataclass
class CotizacionFormal:
    folio: str
    cliente_nombre: str
    datos_contacto: str
    ubicacion: str
    tipo_inmueble: str
    superficie: Superficie
    frecuencia: str
    extras_solicitados: List[Dict[str, float]]  # [{"nombre": "limpieza de vidrios", "horas": 1.0, "costo": 300.0}]
    canal_origen: str = "web"
    estado: EstadoCotizacion = EstadoCotizacion.BORRADOR
    descuento: Descuento = field(default_factory=lambda: Descuento(0.0))
    subtotal: Monto = field(init=False)
    total: Monto = field(init=False)
    horas_persona_sugeridas: float = field(init=False)
    personal_sugerido: int = field(init=False)
    autorizado_por_gerencia: Optional[str] = None
    fecha_creacion: datetime = field(default_factory=datetime.utcnow)
    fecha_respuesta: Optional[datetime] = None
    eventos: List[DomainEvent] = field(default_factory=list)

    def __post_init__(self):
        if not all([self.ubicacion.strip(), self.tipo_inmueble.strip(), self.frecuencia.strip(), self.datos_contacto.strip()]):
            raise DomainError("Faltan campos obligatorios en la solicitud de cotización (CA-01.1, CA-01.2).")
        self._calcular_estimaciones_y_totales()

    def _calcular_estimaciones_y_totales(self):
        horas_base = self.superficie.metros_cuadrados / settings.RENDIMIENTO_M2_PERSONA_HORA
        horas_extras = sum(e.get("horas", 0.0) for e in self.extras_solicitados)
        self.horas_persona_sugeridas = round(horas_base + horas_extras, 2)
        self.personal_sugerido = max(1, math.ceil(self.horas_persona_sugeridas / 4.0))

        costo_base = self.superficie.metros_cuadrados * settings.TARIFA_POR_M2
        costo_extras = sum(e.get("costo", 0.0) for e in self.extras_solicitados)
        self.subtotal = Monto(round(costo_base + costo_extras, 2))
        self.total = self.subtotal.aplicar_porcentaje(self.descuento.porcentaje)

        # RN-02: Verificar si excede 300 m² o $8,000
        limite_spec = CotizacionDentroDeLimiteCoordinadorSpec()
        if not limite_spec.is_satisfied_by((self.superficie.metros_cuadrados, self.total.valor)):
            if self.estado == EstadoCotizacion.BORRADOR and not self.autorizado_por_gerencia:
                self.estado = CotizacionStateMachine.transicionar(self.estado, EstadoCotizacion.PENDIENTE_AUTORIZACION)

    def aplicar_descuento(self, porcentaje: float, rol: str, usuario: str, motivo: str = "Contrato de frecuencia"):
        if self.estado == EstadoCotizacion.ACEPTADA:
            raise DomainError("Una cotización aceptada no puede editarse (CA-05.4).")
        spec = DescuentoAutorizablePorCoordinadorSpec()
        self.descuento = Descuento(porcentaje=porcentaje, motivo=motivo, usuario=usuario)
        self.total = self.subtotal.aplicar_porcentaje(porcentaje)

        if rol.lower() == "coordinador" and not spec.is_satisfied_by(porcentaje):
            self.estado = CotizacionStateMachine.transicionar(self.estado, EstadoCotizacion.PENDIENTE_AUTORIZACION)
            raise DomainError("Descuentos mayores a 10% requieren autorización de gerencia (RN-01, CA-03.2).")

    def autorizar_por_gerencia(self, usuario_gerencia: str):
        self.estado = CotizacionStateMachine.transicionar(self.estado, EstadoCotizacion.AUTORIZADA)
        self.autorizado_por_gerencia = usuario_gerencia

    def enviar_al_cliente(self):
        if self.estado == EstadoCotizacion.PENDIENTE_AUTORIZACION:
            raise DomainError("No se puede enviar una cotización pendiente de autorización de gerencia (CA-04.2).")
        self.estado = CotizacionStateMachine.transicionar(self.estado, EstadoCotizacion.ENVIADA)
        self.fecha_respuesta = datetime.utcnow()

    def aceptar_por_cliente(self) -> "OrdenDeServicio":
        if self.estado == EstadoCotizacion.PENDIENTE_AUTORIZACION:
            raise DomainError("La cotización requiere autorización de gerencia antes de ser aceptada.")
        self.estado = CotizacionStateMachine.transicionar(self.estado, EstadoCotizacion.ACEPTADA)
        self.eventos.append(CotizacionAceptada(folio_cotizacion=self.folio, cliente_id=self.cliente_nombre))
        return OrdenDeServicio(
            folio=f"SRV-{self.folio.split('-')[-1]}",
            folio_cotizacion=self.folio,
            cliente_nombre=self.cliente_nombre,
            ubicacion=self.ubicacion,
            superficie=self.superficie,
            precio_total=self.total,
            duracion_estimada_horas=round(self.horas_persona_sugeridas / self.personal_sugerido, 2),
        )

@dataclass
class OrdenDeServicio:
    folio: str
    folio_cotizacion: str
    cliente_nombre: str
    ubicacion: str
    superficie: Superficie
    precio_total: Monto
    duracion_estimada_horas: float
    estado: EstadoOrdenServicio = EstadoOrdenServicio.GENERADA
    fecha_inicio_programada: Optional[datetime] = None
    fecha_fin_programada: Optional[datetime] = None
    cuadrilla_asignada: Optional[Cuadrilla] = None
    hora_inicio_real: Optional[datetime] = None
    hora_fin_real: Optional[datetime] = None
    incidencias: List[Incidencia] = field(default_factory=list)
    extras: List[ServicioExtra] = field(default_factory=list)
    firma: Optional[FirmaConformidad] = None
    monto_facturable: Optional[Monto] = None
    eventos: List[DomainEvent] = field(default_factory=list)

    def programar(self, fecha_inicio: datetime, cuadrilla: Optional[Cuadrilla] = None):
        fin = fecha_inicio + timedelta(hours=max(1.0, self.duracion_estimada_horas))
        if cuadrilla:
            cuadrilla.asignar_horario(fecha_inicio, fin)
            self.cuadrilla_asignada = cuadrilla
        self.fecha_inicio_programada = fecha_inicio
        self.fecha_fin_programada = fin
        self.estado = OrdenServicioStateMachine.transicionar(self.estado, EstadoOrdenServicio.PROGRAMADA)

    def registrar_inicio(self, marca_tiempo: Optional[datetime] = None):
        self.estado = OrdenServicioStateMachine.transicionar(self.estado, EstadoOrdenServicio.EN_EJECUCION)
        self.hora_inicio_real = marca_tiempo or datetime.utcnow()

    def documentar_incidencia(self, tipo: str, descripcion: str, fotos: List[str]):
        self.incidencias.append(Incidencia(tipo=tipo, descripcion=descripcion, fotos=fotos))

    def solicitar_y_autorizar_extra(self, descripcion: str, costo: float, autorizado: bool):
        extra = ServicioExtra(descripcion=descripcion, costo=Monto(costo), autorizado_por_cliente=autorizado)
        if autorizado:
            extra.fecha_autorizacion = datetime.utcnow()
            self.extras.append(extra)
            self.precio_total = Monto(round(self.precio_total.valor + costo, 2))

    def recalcular_por_superficie_mayor(self, nueva_superficie_m2: float, fotos: List[str], autorizado_cliente: bool):
        if not fotos:
            raise DomainError("El ajuste de superficie exige evidencia fotográfica (CA-15.1).")
        if nueva_superficie_m2 <= self.superficie.metros_cuadrados:
            raise DomainError("La nueva superficie debe ser mayor a la originalmente reportada.")
        if autorizado_cliente:
            proporcion = nueva_superficie_m2 / self.superficie.metros_cuadrados
            self.superficie = Superficie(nueva_superficie_m2)
            self.precio_total = self.precio_total.factor(proporcion)

    def registrar_acceso_denegado(self, evidencia_foto: str):
        if not evidencia_foto.strip():
            raise DomainError("El registro de acceso denegado requiere evidencia fotográfica o nota (CA-13.1).")
        self.estado = OrdenServicioStateMachine.transicionar(self.estado, EstadoOrdenServicio.NO_EJECUTADO_CON_CARGO)
        self.monto_facturable = self.precio_total  # RN-05: 100% de penalización
        if self.cuadrilla_asignada and self.fecha_inicio_programada and self.fecha_fin_programada:
            self.cuadrilla_asignada.liberar_horario(self.fecha_inicio_programada, self.fecha_fin_programada)
        self.eventos.append(AccesoDenegadoRegistrado(folio_orden=self.folio, monto_penalizacion=self.monto_facturable.valor))

    def cancelar(self, fecha_solicitud: datetime, fuerza_mayor: bool = False):
        if not self.fecha_inicio_programada:
            self.estado = OrdenServicioStateMachine.transicionar(self.estado, EstadoOrdenServicio.CANCELADA_SIN_CARGO)
            return
        spec = CancelacionSinPenalizacionSpec()
        sin_costo = fuerza_mayor or spec.is_satisfied_by((fecha_solicitud, self.fecha_inicio_programada))
        if self.cuadrilla_asignada and self.fecha_fin_programada:
            self.cuadrilla_asignada.liberar_horario(self.fecha_inicio_programada, self.fecha_fin_programada)
        if sin_costo:
            self.estado = OrdenServicioStateMachine.transicionar(self.estado, EstadoOrdenServicio.CANCELADA_SIN_CARGO)
            self.monto_facturable = Monto(0.0)
        else:
            self.estado = OrdenServicioStateMachine.transicionar(self.estado, EstadoOrdenServicio.CANCELADA_CON_CARGO)
            self.monto_facturable = self.precio_total.factor(0.50)  # RN-04: 50% de penalización

    def cerrar_servicio(self, firma: FirmaConformidad, hora_fin: Optional[datetime] = None):
        if not self.hora_inicio_real:
            raise DomainError("No puede registrarse el término si no existe un registro de inicio (CA-09.2).")
        for inc in self.incidencias:
            inc.validar_para_cierre()
        self.hora_fin_real = hora_fin or datetime.utcnow()
        self.firma = firma
        nuevo_estado = (
            EstadoOrdenServicio.CERRADA_CONFORMIDAD
            if firma.conformidad
            else EstadoOrdenServicio.CERRADA_INCONFORMIDAD
        )
        self.estado = OrdenServicioStateMachine.transicionar(self.estado, nuevo_estado)
        self.monto_facturable = self.precio_total
        self.eventos.append(
            ServicioCerrado(folio_orden=self.folio, monto_final=self.monto_facturable.valor, con_conformidad=firma.conformidad)
        )