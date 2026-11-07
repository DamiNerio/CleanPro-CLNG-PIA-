from dataclasses import dataclass, field
from datetime import datetime

from src.domain.exceptions import DomainError  # re-exportada por compatibilidad

__all__ = ["DomainError", "Monto", "Superficie", "Descuento", "FirmaConformidad"]


@dataclass(frozen=True)
class Monto:
    """Value Object: cantidad en MXN. Invariante: nunca negativa."""
    valor: float

    def __post_init__(self):
        if self.valor < 0:
            raise DomainError("El monto no puede ser negativo.")

    def aplicar_porcentaje(self, porcentaje: float) -> "Monto":
        return Monto(round(self.valor * (1 - porcentaje / 100.0), 2))

    def factor(self, proporcion: float) -> "Monto":
        return Monto(round(self.valor * proporcion, 2))

    def sumar(self, otro: "Monto") -> "Monto":
        return Monto(round(self.valor + otro.valor, 2))


@dataclass(frozen=True)
class Superficie:
    """Value Object: metros cuadrados del inmueble. Invariante: mayor a cero."""
    metros_cuadrados: float

    def __post_init__(self):
        if self.metros_cuadrados <= 0:
            raise DomainError("La superficie debe ser un valor numérico mayor a cero.")


@dataclass(frozen=True)
class Descuento:
    """Value Object: porcentaje de descuento con su motivo y usuario que lo aplicó."""
    porcentaje: float
    motivo: str = ""
    usuario: str = ""

    def __post_init__(self):
        if not (0 <= self.porcentaje <= 100):
            raise DomainError("El porcentaje de descuento debe estar entre 0 y 100.")


@dataclass(frozen=True)
class FirmaConformidad:
    """Value Object: firma digital del cliente al cierre (US-11)."""
    nombre_firmante: str
    conformidad: bool
    motivo_inconformidad: str = ""
    # default_factory: la fecha se toma al momento de firmar, no al arrancar la app.
    fecha_hora: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        if not self.nombre_firmante.strip():
            raise DomainError("El nombre de quien firma es obligatorio.")
        if not self.conformidad and not self.motivo_inconformidad.strip():
            raise DomainError("La inconformidad requiere un motivo obligatorio.")
