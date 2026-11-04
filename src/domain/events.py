from dataclasses import dataclass, field
from datetime import datetime

@dataclass(frozen=True)
class DomainEvent:
    occurred_on: datetime = field(default_factory=datetime.utcnow)

@dataclass(frozen=True)
class CotizacionAceptada(DomainEvent):
    folio_cotizacion: str = ""
    cliente_id: str = ""

@dataclass(frozen=True)
class AusenciaReportada(DomainEvent):
    folio_orden: str = ""
    id_integrante_ausente: str = ""
    id_integrante_reemplazo: str = ""
    motivo: str = ""

@dataclass(frozen=True)
class AccesoDenegadoRegistrado(DomainEvent):
    folio_orden: str = ""
    monto_penalizacion: float = 0.0

@dataclass(frozen=True)
class ServicioCerrado(DomainEvent):
    folio_orden: str = ""
    monto_final: float = 0.0
    con_conformidad: bool = True