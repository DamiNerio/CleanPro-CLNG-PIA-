# CleanPro — (PIA CLNG)

Solución integral de software basada en **Domain-Driven Design (DDD)**, patrón **Specification**, **State Machine**, **portales web diferenciados por rol** y **API REST documentada con OpenAPI/Swagger** para el **Caso de Negocio 12: CleanPro** (Servicios de limpieza residencial y empresarial).

---

## Datos

* **Institución:** Universidad Autónoma de Nuevo León (UANL) — Facultad de Ingeniería Mecánica y Eléctrica (FIME)
* **Unidad de Aprendizaje:** Componentes de Lógica de Negocios (CLNG) — Semestre Agosto-Diciembre 2026
* **Docente:** Ing. Miguel Ángel Gómez Marroquín
* **Equipo:** 12 | **Grupo:** 004 | **Hora:** Martes M4-M6

| Integrante | Matrícula | Carrera |
| :--- | :--- | :--- |
| **Camila Trujillo Quintanilla** | 2162775 | Ingeniero en Tecnología de Software (ITS) |
| **Cesar Damian Nerio Gonzalez** | 2161751 | Ingeniero en Tecnología de Software (ITS) |
| **Jesús Enrique López Martínez** | 2162022 | Ingeniero en Tecnología de Software (ITS) |

---

## Enlaces Oficiales de Entrega

* **Repositorio GitHub:** `https://github.com/DamiNerio/cleanpro-CLNG-PIA-`
* **Portal Público del Cliente (Producción Render):** `https://cleanpro-bjr6.onrender.com/`
* **Intranet Operativa y Administrativa (Personal CleanPro):** `https://cleanpro-bjr6.onrender.com/admin`
* **Swagger UI / OpenAPI Activo en Producción:** `https://cleanpro-bjr6.onrender.com/docs`
* **Estado del servicio y tipo de persistencia:** `https://cleanpro-bjr6.onrender.com/health`

## Estructura del Repositorio

```
docs/
  BRD.md                      Análisis: entrevista, BRD, 19 User Stories + Gherkin, glosario y matriz de trazabilidad
  bpmn/                       Diagrama BPMN del proceso CleanPro
  architecture/               ADRs, DDD y patrones, SOLID, diagramas UML/Mermaid
  api/                        Especificación OpenAPI
src/
  domain/                     Entidades, Value Objects, Specifications, State Machines, eventos, excepciones y puerto de repositorio
  application/                Casos de uso (Service Layer)
  infrastructure/             Configuración (variables de entorno), mappers y repositorios (SQLAlchemy y memoria)
  api/                        FastAPI: endpoints REST, portal del cliente (index.html) e intranet (admin.html)
tests/                        Pruebas unitarias (dominio, servicios) e integración (persistencia y API)
docker/initdb/                Script que crea la base de pruebas en PostgreSQL
.github/workflows/ci.yml      Pipeline CI/CD
```

## Configuración por Variables de Entorno (12-Factor App)

El archivo `.env.example` y la sección *Environment Variables* de Render parametrizan la base de datos y las políticas de negocio sin exponer secretos reales ni requerir cambios de programación (CA-02.2):

| Variable | Valor por Defecto | Regla Asociada | Descripción |
| :--- | :--- | :--- | :--- |
| `DATABASE_URL` | `sqlite:///./cleanpro.db` | ADR-006 | Base de datos. SQLite en local; PostgreSQL en Docker (`postgresql://...@db:5432/cleanpro_db`) y Render (Internal Database URL). `memory` usa el repositorio en memoria. |
| `PYTHON_VERSION` | `3.11.9` | Despliegue Render | Versión de Python en la nube para uso de binarios precompilados (*wheels*). |
| `MAX_DESCUENTO_COORDINADOR` | `10.0` | **RN-01** | Porcentaje máximo de descuento que autoriza un coordinador. |
| `MAX_M2_COORDINADOR` | `300.0` | **RN-02** | Superficie máxima en m² que confirma un coordinador sin gerencia. |
| `MAX_MONTO_COORDINADOR` | `8000.0` | **RN-02** | Monto máximo en MXN que confirma un coordinador sin gerencia. |
| `RENDIMIENTO_M2_PERSONA_HORA` | `60.0` | **US-02** | Rendimiento en m² limpiados por persona cada hora. |
| `TARIFA_POR_M2` | `25.0` | **US-02, RN-07** | Tarifa base por m² para cotización y recálculo proporcional. |
| `HORAS_CANCELACION_SIN_COSTO` | `24` | **RN-04** | Horas mínimas de anticipación para cancelar sin cargo del 50%. |
| `MAX_REPROGRAMACIONES_MES` | `2` | **RN-08** | Reprogramaciones mensuales antes de alertar a gerencia. |
| `SLA_RESPUESTA_HORAS` | `4.0` | **RN-03** | Tiempo máximo en horas hábiles para responder cotizaciones. |
| `ZONA_HORARIA_OFFSET_HORAS` | `-6` | **RN-04** | Hora local de Monterrey para calcular la anticipación de cancelaciones. |

---

## Instalación y Ejecución Local (Windows / PowerShell)

> Se recomienda **Python 3.11 o 3.12** (las mismas versiones que usan Render, Docker y GitHub Actions).

### 1. Clonar el repositorio y activar el entorno virtual
```powershell
git clone https://github.com/DamiNerio/cleanpro-CLNG-PIA-.git
cd cleanpro-CLNG-PIA-
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### 2. Ejecutar la suite de pruebas y verificar cobertura (>= 80%)
```powershell
$env:PYTHONPATH="."
python -m pytest --cov=src --cov-report=term-missing --cov-fail-under=80
```
Las pruebas usan SQLite en memoria; no necesitan PostgreSQL.

### 3. Iniciar el servidor web y API REST
```powershell
python -m uvicorn src.api.main:app --reload --port 8000
```
* **Portal del Cliente:** `http://localhost:8000/`
* **Intranet Administrativa:** `http://localhost:8000/admin`
* **Swagger UI (API):** `http://localhost:8000/docs`

Los datos se guardan en `cleanpro.db` (SQLite) y se conservan entre reinicios.

### 4. Regenerar la especificación OpenAPI
```powershell
python scripts/exportar_openapi.py
```
Genera `docs/api/openapi.json` directamente desde el código.

---

## Ejecución con Docker Compose (PostgreSQL + App + Tests)

```powershell
docker compose up --build
```
* `db`: PostgreSQL 15 con volumen persistente (`pgdata`) y una base aparte `cleanpro_test` para las pruebas.
* `app`: la API en `http://localhost:8000` conectada a PostgreSQL.
* `tests`: corre toda la suite con cobertura contra PostgreSQL y termina.

Volver a correr solo las pruebas: `docker compose run --rm tests`. Detener: `docker compose down` (agregar `-v` para borrar los datos).

---

## Pipeline CI/CD (GitHub Actions)

Cada `push` a `main`/`develop` y cada *pull request* ejecuta:
1. **Pruebas + cobertura (SQLite):** toda la suite con compuerta `--cov-fail-under=80` y reporte `coverage.xml` como artefacto.
2. **Pruebas de integración (PostgreSQL):** la API contra un PostgreSQL real levantado como servicio.
3. **Construcción de la imagen Docker:** solo si las dos anteriores pasan.

Render redespliega automáticamente la rama `main`.

---

## Despliegue en Render

* **Build Command:** `pip install -r requirements.txt`
* **Start Command:** `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
* **Environment:** `PYTHON_VERSION=3.11.9`, las variables de `.env.example` y `DATABASE_URL`.
* **Base de datos:** en Render crear *New → PostgreSQL* (plan Free), copiar su **Internal Database URL** y pegarla en la variable `DATABASE_URL` del servicio web. Sin esta variable la app usa SQLite, que Render borra cuando el servicio se reinicia.
* Verificar en `/health` que diga `"persistencia": "RepositorioSQLAlchemy"`.

---

## Endpoints Principales

| Módulo | Endpoint | User Story / Regla |
| :--- | :--- | :--- |
| Cotización | `POST /api/cotizaciones` · `GET /api/cotizaciones/{folio}` | US-01, US-02 |
| | `PATCH /api/cotizaciones/{folio}/descuento` | US-03, RN-01 (403 si requiere gerencia) |
| | `POST /api/cotizaciones/{folio}/autorizar` · `/descartar` | US-04 |
| | `POST /api/cotizaciones/{folio}/aceptar` · `/rechazar` | US-05 |
| Programación | `POST /api/ordenes/{folio}/programar` · `GET /api/agenda` · `GET /api/cuadrillas` | US-06, US-07, US-08 (409 si hay traslape) |
| Ejecución | `POST /api/ordenes/{folio}/iniciar` · `/incidencias` · `/cerrar` | US-09, US-10, US-11 |
| Excepciones | `POST /api/ordenes/{folio}/ausencia` | US-12, US-17 |
| | `POST /api/ordenes/{folio}/acceso-denegado` | US-13, RN-05 |
| | `POST /api/ordenes/{folio}/extras` · `/ajuste-superficie` | US-14, US-15, RN-06, RN-07 |
| | `POST /api/ordenes/{folio}/cancelar` · `/reprogramar` | US-16, RN-04, RN-08 |
| Administración | `POST /api/facturables/{folio}/facturar` · `GET /api/administracion/kpis` · `GET /api/estado` | US-18, US-19, RN-09 |
| Portal del cliente | `GET /api/clientes/solicitudes?contacto=...` | ADR-008 |

Códigos de error: **404** recurso inexistente · **403** requiere autorización de gerencia · **409** transición de estado inválida o traslape de agenda · **422** dato o regla de negocio inválida.

---

## Guion de Demostración en Vivo (el profesor actúa como cliente)

1. **Cliente (`/`):** solicita cotización de una oficina de 240 m² con limpieza de vidrios → recibe folio y precio al instante (US-01, US-02).
2. **Coordinador (`/admin` → pestaña 1):** intenta un 15% de descuento → el sistema lo bloquea y lo manda a Gerencia (RN-01).
3. **Gerencia (`/admin` → pestaña 3):** aprueba la excepción (US-04).
4. **Cliente (`/`):** escribe su teléfono/correo, ve solo su cotización y la acepta (US-05).
5. **Coordinador:** programa la fecha y asigna la cuadrilla C-05; intentar la misma cuadrilla en un horario traslapado es rechazado (US-06, US-07).
6. **Supervisor (pestaña 2):** registra inicio, una incidencia con foto, un servicio extra autorizado y una ausencia que llega a Nómina (US-09, US-10, US-12, US-14, US-17).
7. **Cliente (`/`):** firma de conformidad (US-11).
8. **Administración (pestaña 3):** el servicio aparece en facturables y se emite la factura (US-18, RN-09); KPIs actualizados (US-19).
9. **Excepciones:** con otra orden, mostrar acceso denegado (cobro 100%, RN-05) y cancelación con menos de 24 h (cobro 50%, RN-04).
10. **Calidad:** mostrar el pipeline en verde en GitHub Actions y `/docs` en producción.
