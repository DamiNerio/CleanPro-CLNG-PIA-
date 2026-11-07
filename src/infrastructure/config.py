import os
from dataclasses import dataclass

@dataclass(frozen=True)
class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./cleanpro.db")
    MAX_DESCUENTO_COORDINADOR: float = float(os.getenv("MAX_DESCUENTO_COORDINADOR", "10.0"))
    MAX_M2_COORDINADOR: float = float(os.getenv("MAX_M2_COORDINADOR", "300.0"))
    MAX_MONTO_COORDINADOR: float = float(os.getenv("MAX_MONTO_COORDINADOR", "8000.0"))
    RENDIMIENTO_M2_PERSONA_HORA: float = float(os.getenv("RENDIMIENTO_M2_PERSONA_HORA", "60.0"))
    TARIFA_POR_M2: float = float(os.getenv("TARIFA_POR_M2", "25.0"))
    HORAS_CANCELACION_SIN_COSTO: int = int(os.getenv("HORAS_CANCELACION_SIN_COSTO", "24"))
    MAX_REPROGRAMACIONES_MES: int = int(os.getenv("MAX_REPROGRAMACIONES_MES", "2"))
    SLA_RESPUESTA_HORAS: float = float(os.getenv("SLA_RESPUESTA_HORAS", "4.0"))
    # Monterrey usa UTC-6 todo el año; las fechas de programación se capturan en hora local.
    ZONA_HORARIA_OFFSET_HORAS: float = float(os.getenv("ZONA_HORARIA_OFFSET_HORAS", "-6"))

settings = Settings()