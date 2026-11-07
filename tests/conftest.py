import os

# Las pruebas usan SQLite en memoria salvo que el entorno indique otra base
# (por ejemplo PostgreSQL dentro de Docker Compose). Debe definirse antes de
# importar src.api.main, que crea el repositorio al cargarse.
os.environ.setdefault("DATABASE_URL", "sqlite://")

import pytest  # noqa: E402

from src.infrastructure.repositories import RepositorioEnMemoria  # noqa: E402
from tests.helpers import Servicios  # noqa: E402


@pytest.fixture
def repo():
    return RepositorioEnMemoria()


@pytest.fixture
def srv(repo):
    return Servicios(repo)
