"""Regenera docs/api/openapi.json a partir del código (la especificación siempre coincide con la API).

Uso:  python scripts/exportar_openapi.py
"""
import json
import os
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ))
os.environ.setdefault("DATABASE_URL", "memory")

from src.api.main import app  # noqa: E402

destino = RAIZ / "docs" / "api" / "openapi.json"
destino.write_text(json.dumps(app.openapi(), ensure_ascii=False, indent=2), encoding="utf-8")
anterior = destino.with_suffix(".yaml")
if anterior.exists():
    anterior.unlink()  # la versión YAML escrita a mano quedó desactualizada
print(f"OpenAPI exportado en {destino}")
