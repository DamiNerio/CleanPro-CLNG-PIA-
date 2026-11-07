from abc import ABC, abstractmethod
from datetime import datetime
from typing import Generic, TypeVar, List, Tuple
from src.infrastructure.config import settings

T = TypeVar("T")

class Specification(ABC, Generic[T]):
    """Regla de negocio evaluable y combinable: spec_a & spec_b, spec_a | spec_b, ~spec."""

    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        pass

    def __and__(self, other: "Specification[T]") -> "Specification[T]":
        return AndSpecification(self, other)

    def __or__(self, other: "Specification[T]") -> "Specification[T]":
        return OrSpecification(self, other)

    def __invert__(self) -> "Specification[T]":
        return NotSpecification(self)


class AndSpecification(Specification[T]):
    def __init__(self, left: Specification[T], right: Specification[T]):
        self.left, self.right = left, right

    def is_satisfied_by(self, candidate: T) -> bool:
        return self.left.is_satisfied_by(candidate) and self.right.is_satisfied_by(candidate)


class OrSpecification(Specification[T]):
    def __init__(self, left: Specification[T], right: Specification[T]):
        self.left, self.right = left, right

    def is_satisfied_by(self, candidate: T) -> bool:
        return self.left.is_satisfied_by(candidate) or self.right.is_satisfied_by(candidate)


class NotSpecification(Specification[T]):
    def __init__(self, spec: Specification[T]):
        self.spec = spec

    def is_satisfied_by(self, candidate: T) -> bool:
        return not self.spec.is_satisfied_by(candidate)

class DescuentoAutorizablePorCoordinadorSpec(Specification[float]):
    """RN-01: El coordinador sólo autoriza descuentos de hasta 10%."""
    def __init__(self, limite: float = settings.MAX_DESCUENTO_COORDINADOR):
        self.limite = limite

    def is_satisfied_by(self, porcentaje: float) -> bool:
        return 0.0 <= porcentaje <= self.limite

class SuperficieDentroDeLimiteSpec(Specification[Tuple[float, float]]):
    """RN-02 (parte 1): superficie <= 300 m². Candidato: (superficie_m2, monto_total)."""
    def __init__(self, max_m2: float = settings.MAX_M2_COORDINADOR):
        self.max_m2 = max_m2

    def is_satisfied_by(self, candidate: Tuple[float, float]) -> bool:
        return candidate[0] <= self.max_m2


class MontoDentroDeLimiteSpec(Specification[Tuple[float, float]]):
    """RN-02 (parte 2): monto <= $8,000. Candidato: (superficie_m2, monto_total)."""
    def __init__(self, max_monto: float = settings.MAX_MONTO_COORDINADOR):
        self.max_monto = max_monto

    def is_satisfied_by(self, candidate: Tuple[float, float]) -> bool:
        return candidate[1] <= self.max_monto


class CotizacionDentroDeLimiteCoordinadorSpec(Specification[Tuple[float, float]]):
    """RN-02: El coordinador confirma servicios de hasta 300 m² y $8,000 sin aprobación adicional.

    Se construye combinando dos especificaciones con el operador & (AND).
    """
    def __init__(self, max_m2: float = settings.MAX_M2_COORDINADOR, max_monto: float = settings.MAX_MONTO_COORDINADOR):
        self.max_m2 = max_m2
        self.max_monto = max_monto
        self._regla = SuperficieDentroDeLimiteSpec(max_m2) & MontoDentroDeLimiteSpec(max_monto)

    def is_satisfied_by(self, candidate: Tuple[float, float]) -> bool:
        return self._regla.is_satisfied_by(candidate)

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