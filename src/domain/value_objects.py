from dataclasses import dataclass
from datetime import datetime

class DomainError(ValueError):
    """Excepción base para violaciones de invariantes del dominio CleanPro."""
    pass

@dataclass(frozen=True)
class Monto:
    valor: float

    def __post_init__(self):
        if self.valor < 0:
            raise DomainError("El monto no puede ser negativo.")

    def aplicar_porcentaje(self, porcentaje: float) -> "Monto":
        return Monto(round(self.valor * (1 - porcentaje / 100.0), 2))

    def factor(self, proporcion: float) -> "Monto":
        return Monto(round(self.valor * proporcion, 2))

@dataclass(frozen=True)
class Superficie:
    metros_cuadrados: float

    def __post_init__(self):
        if self.metros_cuadrados <= 0:
            raise DomainError("La superficie debe ser un valor numérico mayor a cero.")

@dataclass(frozen=True)
class Descuento:
    porcentaje: float
    motivo: str = ""
    usuario: str = ""

    def __post_init__(self):
        if not (0 <= self.porcentaje <= 100):
            raise DomainError("El porcentaje de descuento debe estar entre 0 y 100.")

@dataclass(frozen=True)
class FirmaConformidad:
    nombre_firmante: str
    conformidad: bool
    motivo_inconformidad: str = ""
    fecha_hora: datetime = datetime.utcnow()

    def __post_init__(self):
        if not self.nombre_firmante.strip():
            raise DomainError("El nombre de quien firma es obligatorio.")
        if not self.conformidad and not self.motivo_inconformidad.strip():
            raise DomainError("La inconformidad requiere un motivo obligatorio.")