from abc import ABC, abstractmethod
from datetime import datetime
from typing import Generic, TypeVar, List, Tuple
from src.infrastructure.config import settings

T = TypeVar("T")

class Specification(ABC, Generic[T]):
    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        pass

class DescuentoAutorizablePorCoordinadorSpec(Specification[float]):
    """RN-01: El coordinador sólo autoriza descuentos de hasta 10%."""
    def __init__(self, limite: float = settings.MAX_DESCUENTO_COORDINADOR):
        self.limite = limite

    def is_satisfied_by(self, porcentaje: float) -> bool:
        return 0.0 <= porcentaje <= self.limite

class CotizacionDentroDeLimiteCoordinadorSpec(Specification[Tuple[float, float]]):
    """RN-02: El coordinador confirma servicios de hasta 300 m² o $8,000 sin aprobación adicional."""
    def __init__(self, max_m2: float = settings.MAX_M2_COORDINADOR, max_monto: float = settings.MAX_MONTO_COORDINADOR):
        self.max_m2 = max_m2
        self.max_monto = max_monto

    def is_satisfied_by(self, candidate: Tuple[float, float]) -> bool:
        superficie_m2, monto_total = candidate
        return superficie_m2 <= self.max_m2 and monto_total <= self.max_monto

class CancelacionSinPenalizacionSpec(Specification[Tuple[datetime, datetime]]):
    """RN-04: Cancelación o reprogramación sin costo con 24 horas o más de anticipación."""
    def __init__(self, horas_minimas: int = settings.HORAS_CANCELACION_SIN_COSTO):
        self.horas_minimas = horas_minimas

    def is_satisfied_by(self, candidate: Tuple[datetime, datetime]) -> bool:
        fecha_solicitud, fecha_programada = candidate
        diferencia_horas = (fecha_programada - fecha_solicitud).total_seconds() / 3600.0
        return diferencia_horas >= self.horas_minimas

class ClienteSuperaLimiteReprogramacionesSpec(Specification[int]):
    """RN-08: Más de 2 reprogramaciones en un mes requiere alerta a gerencia."""
    def __init__(self, max_reprogramaciones: int = settings.MAX_REPROGRAMACIONES_MES):
        self.max_reprogramaciones = max_reprogramaciones

    def is_satisfied_by(self, conteo_mes: int) -> bool:
        return conteo_mes > self.max_reprogramaciones

class CuadrillaDisponibleSpec(Specification[Tuple[datetime, datetime, List[Tuple[datetime, datetime]]]]):
    """CA-06.3 y CA-07.2: Verifica que una cuadrilla no tenga servicios traslapados."""
    def is_satisfied_by(self, candidate: Tuple[datetime, datetime, List[Tuple[datetime, datetime]]]) -> bool:
        inicio_nuevo, fin_nuevo, ventanas_ocupadas = candidate
        for inicio_existente, fin_existente in ventanas_ocupadas:
            if inicio_nuevo < fin_existente and fin_nuevo > inicio_existente:
                return False
        return True