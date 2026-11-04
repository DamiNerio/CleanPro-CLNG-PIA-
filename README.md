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

## Configuración por Variables de Entorno (12-Factor App)

El archivo `.env.example` y la sección *Environment Variables* en Render parametrizan todas las políticas de negocio de CleanPro sin exponer secretos reales ni requerir cambios de programación (CA-02.2):

| Variable | Valor por Defecto | Regla Asociada | Descripción |
| :--- | :--- | :--- | :--- |
| `PYTHON_VERSION` | `3.11.9` | Despliegue Render | Versión de Python en la nube para uso de binarios precompilados (*wheels*). |
| `DATABASE_URL` | `sqlite:///./cleanpro.db` | Infraestructura | Cadena de conexión a base de datos (SQLite o PostgreSQL en Docker). |
| `MAX_DESCUENTO_COORDINADOR` | `10.0` | **RN-01** | Porcentaje máximo de descuento que autoriza un coordinador (hasta 10%). |
| `MAX_M2_COORDINADOR` | `300.0` | **RN-02** | Superficie máxima en m2 que confirma un coordinador sin gerencia. |
| `MAX_MONTO_COORDINADOR` | `8000.0` | **RN-02** | Monto máximo en MXN que confirma un coordinador sin gerencia. |
| `RENDIMIENTO_M2_PERSONA_HORA` | `60.0` | **US-02** | Rendimiento en m2 limpiados por persona cada hora. |
| `TARIFA_POR_M2` | `25.0` | **US-02, RN-07** | Tarifa base por metro cuadrado para cotización y recálculo proporcional. |
| `HORAS_CANCELACION_SIN_COSTO` | `24` | **RN-04** | Horas mínimas de anticipación para cancelar o reprogramar sin cargo del 50%. |
| `MAX_REPROGRAMACIONES_MES` | `2` | **RN-08** | Límite de reprogramaciones mensuales antes de alertar a gerencia. |
| `SLA_RESPUESTA_HORAS` | `4.0` | **RN-03** | Tiempo máximo en horas hábiles para responder solicitudes de cotización. |

---

## Instrucciones de Instalación y Ejecución Local

### 1. Clonar el repositorio y activar el entorno virtual
```powershell
git clone https://github.com/DamiNerio/CleanPro-PIA-CLNG-.git
cd CleanPro-PIA-CLNG-
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
*Resultado actual verificado:* **82.25% de cobertura total** con todas las pruebas unitarias y de integración en verde.

### 3. Iniciar el servidor web y API REST
```powershell
python -m uvicorn src.api.main:app --reload --port 8000
```
* **Portal del Cliente:** `http://localhost:8000/`
* **Intranet Administrativa:** `http://localhost:8000/admin`
* **Swagger UI (API):** `http://localhost:8000/docs`

---

## Ejecución con Docker Compose (DB + App + Tests)

Para levantar la base de datos PostgreSQL, el servidor de la aplicación y ejecutar el contenedor de pruebas en un entorno reproducible:

```powershell
docker compose up --build
```

Para detener y limpiar los contenedores:
```powershell
docker compose down
```

---

## Configuración de Despliegue en Render

El servicio web se encuentra desplegado en **Render** conectado directamente a la rama `main` del repositorio de GitHub con los siguientes parámetros:
* **Name:** `CleanPro`
* **Language:** `Python 3` (`PYTHON_VERSION = 3.11.9`)
* **Build Command:** `pip install -r requirements.txt`
* **Start Command:** `uvicorn src.api.main:app --host 0.0.0.0 --port $PORT`
* **Environment Variables:** Cargadas desde `.env.example`.