# CleanPro — (PIA CLNG)

![CI/CD Pipeline](https://img.shields.io/badge/CI%2FCD-GitHub_Actions-2088FF?logo=github-actions&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/OpenAPI-Swagger_UI-009688?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

Solución integral de software basada en **Domain-Driven Design (DDD)**, patrón **Specification**, **State Machine** y **API REST documentada con OpenAPI/Swagger** para el **Caso de Negocio 12: CleanPro** (Servicios de limpieza residencial y empresarial).

---

## Datos

* **Institución:** Universidad Autónoma de Nuevo León (UANL) — Facultad de Ingeniería Mecánica y Eléctrica (FIME)
* **Unidad de Aprendizaje:** Componentes de Lógica de Negocios (CLN) — Semestre Agosto-Diciembre 2026
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

## Configuración por Variables de Entorno (12-Factor App)

El archivo `.env.example` parametriza todas las políticas y límites de negocio de CleanPro sin exponer secretos reales ni requerir cambios de código (CA-02.2):

| Variable | Valor por Defecto | Regla Asociada | Descripción |
| :--- | :--- | :--- | :--- |
| `DATABASE_URL` | `sqlite:///./cleanpro.db` | Infraestructura | Cadena de conexión a BD (SQLite local o PostgreSQL en Docker). |
| `MAX_DESCUENTO_COORDINADOR` | `10.0` | **RN-01** | Porcentaje máximo de descuento que autoriza un coordinador (≤10%). |
| `MAX_M2_COORDINADOR` | `300.0` | **RN-02** | Superficie máxima en m² que confirma un coordinador sin gerencia. |
| `MAX_MONTO_COORDINADOR` | `8000.0` | **RN-02** | Monto máximo en MXN que confirma un coordinador sin gerencia. |
| `RENDIMIENTO_M2_PERSONA_HORA` | `60.0` | **US-02** | Rendimiento en m² limpiados por persona cada hora. |
| `TARIFA_POR_M2` | `25.0` | **US-02, RN-07** | Tarifa base por metro cuadrado para cotización y recálculo proporcional. |
| `HORAS_CANCELACION_SIN_COSTO` | `24` | **RN-04** | Horas mínimas de anticipación para cancelar o reprogramar sin penalización del 50%. |
| `MAX_REPROGRAMACIONES_MES` | `2` | **RN-08** | Límite de reprogramaciones mensuales antes de alertar a gerencia. |
| `SLA_RESPUESTA_HORAS` | `4.0` | **RN-03** | Tiempo máximo en horas hábiles para responder solicitudes de cotización. |

---

## Instrucciones de Instalación y Ejecución Local

### 1. Clonar el repositorio y preparar el entorno virtual
```bash
git clone https://github.com/DamiNerio/cleanpro-CLNG-PIA-.git
cd CleanPro-CLNG-PIA-
cp .env.example .env
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Iniciar el servidor API REST
```bash
uvicorn src.api.main:app --reload --port 8000
```
* **Swagger UI interactivo:** Abrir en el navegador `http://localhost:8000/docs`
* **Esquema OpenAPI JSON:** `http://localhost:8000/openapi.json`

### 3. Ejecutar la suite de pruebas y verificar cobertura ($\ge 80\%$)
```bash
pytest --cov=src --cov-report=term-missing --cov-fail-under=80
```

---

## Ejecución con Docker Compose (`DB + App + Tests`)

Para levantar la base de datos PostgreSQL, la aplicación web y ejecutar automáticamente la suite de pruebas en contenedores aislados y reproducibles:

```bash
docker compose up --build
```

Para ejecutar únicamente el contenedor de pruebas verificando el umbral de cobertura del $80\%$:

```bash
docker compose run --rm tests
```