# Telefónica Prepago: recargas, monitoreo y reportes

Aplicación de demostración para procesar recargas, consultar un estado de red
simulado y registrar fallas de acceso a Internet Movistar. Está compuesta por
una API FastAPI, una base de datos SQLite y un dashboard Streamlit que se abre
en un navegador.

## Funcionalidades

- **Recargas:** procesa montos permitidos, asigna fecha/hora y evita duplicados
  mediante un identificador de transacción único.
- **Monitoreo de red:** consulta la última recarga asociada a un MSISDN y devuelve
  un estado simulado según la ubicación.
- **Reportes de Internet:** registra y lista reportes de fallas de acceso a
  Internet.
- **Dashboard:** permite aplicar recargas, monitorear el estado de red y
  registrar fallas desde tres pestañas.
- **Integración con bots:** permite consultar por HTTP GET las recargas
  procesadas y los últimos reportes de fallas de Internet. Los endpoints de
  lectura requieren API Key.

## Arquitectura

- `models/`: esquemas Pydantic y consultas SQLite parametrizadas.
- `controllers/`: endpoints FastAPI, autenticación e integración de datos.
- `views/`: interfaz Streamlit.
- `api.py`: punto de entrada de FastAPI.
- `dashboard.py`: punto de entrada del dashboard.

SQLite crea las tablas cuando inicia la API. De forma predeterminada, la base se
guarda como `prepago.db` en esta carpeta. No se debe borrar si se quiere
conservar el historial.

## Requisitos

- Python 3.10 o posterior.
- Las dependencias declaradas en `requirements.txt`.

## Instalación y ejecución

Desde PowerShell, abre la carpeta `Telefonica_TDW`:

```powershell
cd "C:\Users\Lenovo\Clases_Unexpo\Inteligencia_Artificial\practica_python\IAProfessor\Telefonica_TDW"
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

### Iniciar la API

En una terminal, configura una clave local y ejecuta FastAPI:

```powershell
$env:RECHARGE_API_KEY = Read-Host "API Key local"
python -m uvicorn api:app --reload
```

La API estará disponible en `http://127.0.0.1:8000`. La documentación
interactiva de OpenAPI/Swagger se encuentra en `http://127.0.0.1:8000/docs`.

Opcionalmente, antes de iniciar la API, configura otra ubicación para la base:

```powershell
$env:DATABASE_PATH = "C:\ruta\prepago.db"
```

### Iniciar el dashboard

En una segunda terminal, desde la misma carpeta:

```powershell
.\.venv\Scripts\Activate.ps1
$env:RECHARGE_API_URL = "http://127.0.0.1:8000"
python -m streamlit run dashboard.py
```

Streamlit abre `http://localhost:8501`. Ingresa en el panel lateral la misma API
Key configurada en la terminal de la API. Si se prefiere, esa dirección puede
abrirse manualmente en otro navegador de la misma computadora.

### Configuración del simulador de red

Por defecto, las ubicaciones `Guatire` y `Valencia` se muestran como degradadas.
Para cambiar esa lista, configura `SIMULATED_DEGRADED_LOCATIONS` antes de iniciar
la API, con nombres separados por comas:

```powershell
$env:SIMULATED_DEGRADED_LOCATIONS = "Guatire,Valencia,Maracay"
```

Esta función es una simulación basada en la ubicación de la última recarga; no
consulta telemetría ni sistemas reales de monitoreo de estaciones.

## Autenticación

Todas las rutas que leen o escriben registros requieren el header
`X-API-Key`. El valor debe coincidir con `RECHARGE_API_KEY` en el proceso de la
API. Si la clave no está configurada en el servidor, las rutas protegidas
responden `503`; si falta o no coincide, responden `401`.

No escribas claves reales en el código, en este README ni en el repositorio. Para
la demostración local, solicítala por consola:

```powershell
$env:RECHARGE_API_KEY = Read-Host "API Key"
$headers = @{ "X-API-Key" = $env:RECHARGE_API_KEY }
```

Los errores HTTP se devuelven como Problem Details, con tipo de contenido
`application/problem+json`.

## API de recargas

### Aplicar una recarga

`POST /api/v1/recharges/apply`

Requiere `X-API-Key`. Cuerpo JSON:

| Campo | Tipo | Reglas |
|---|---|---|
| `msisdn` | string | Número del cliente |
| `amount` | number | Únicamente `50`, `100`, `200` o `500` |
| `network_type` | string | Únicamente `4G` o `5G` |
| `location` | string | Zona o ciudad |
| `transaction_id` | string | Identificador único de la transacción |

Ejemplo PowerShell:

```powershell
$body = @{
    msisdn = "04141234567"
    amount = 100
    network_type = "4G"
    location = "Caracas"
    transaction_id = [guid]::NewGuid().ToString()
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/api/v1/recharges/apply" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $body
```

Respuestas principales:

- `201 Created`: recarga guardada; incluye el `timestamp`.
- `400 Bad Request`: cuerpo inválido, monto o red no permitidos.
- `401 Unauthorized`: API Key ausente o inválida.
- `409 Conflict`: `transaction_id` ya procesado; no se crea otra recarga.
- `503 Service Unavailable`: la API no tiene configurada la clave.

### Leer las recargas procesadas

`GET /api/v1/recharges/stats`

Requiere `X-API-Key`. Devuelve todos los registros procesados en la propiedad
`recharges`, ordenados del más antiguo al más reciente:

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/api/v1/recharges/stats" `
  -Headers $headers
```

Este endpoint lista recargas **procesadas correctamente**. No representa un
registro de intentos de recarga rechazados ni de fallas de cobro.

### Consultar estado de red de un cliente

`GET /api/v1/recharges/customer/status/{msisdn}`

Requiere `X-API-Key`. Busca la última recarga del MSISDN y devuelve sus datos
junto con `network_status.status` (`OPERATIONAL` o `DEGRADED`) y una explicación.
Si el MSISDN no tiene recargas, responde `404 Not Found`.

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/api/v1/recharges/customer/status/04141234567" `
  -Headers $headers
```

## API de reportes de fallas de Internet

### Crear un reporte

`POST /api/v1/reports/internet-failures`

Requiere `X-API-Key`. Cuerpo JSON:

| Campo | Tipo | Reglas |
|---|---|---|
| `msisdn` | string | De 7 a 20 caracteres |
| `location` | string | De 2 a 120 caracteres |
| `network_type` | string | `4G` o `5G` |
| `failure_type` | string | `NO_INTERNET`, `INTERMITTENT`, `SLOW` o `OTHER` |
| `description` | string | De 10 a 1200 caracteres |

Ejemplo PowerShell:

```powershell
$body = @{
    msisdn = "04141234567"
    location = "Guarenas"
    network_type = "4G"
    failure_type = "SLOW"
    description = "La navegación está lenta desde esta mañana."
} | ConvertTo-Json

Invoke-RestMethod -Method Post `
  -Uri "http://127.0.0.1:8000/api/v1/reports/internet-failures" `
  -Headers $headers `
  -ContentType "application/json" `
  -Body $body
```

La API genera automáticamente `report_id` y `reported_at`, guarda el reporte en
SQLite con estado inicial `OPEN` y responde `201 Created`. Los errores de
validación responden `400 Bad Request`.

### Leer reportes para un bot

`GET /api/v1/reports/internet-failures`

Requiere `X-API-Key`. Devuelve la propiedad `reports` con los últimos 50
reportes, del más reciente al más antiguo. Cada elemento contiene folio, MSISDN,
ubicación, red, tipo, descripción, estado y fecha.

```powershell
Invoke-RestMethod `
  -Uri "http://127.0.0.1:8000/api/v1/reports/internet-failures" `
  -Headers $headers
```

### Ejemplo Python para conectar un bot por GET

Instala `requests` si el bot se ejecuta en otro entorno:

```powershell
python -m pip install requests
```

El bot debe recibir `RECHARGE_API_KEY` y `RECHARGE_API_URL` desde variables de
entorno o desde un gestor seguro de secretos. Ejemplo:

```python
import os

import requests

base_url = os.getenv("RECHARGE_API_URL", "http://127.0.0.1:8000").rstrip("/")
headers = {"X-API-Key": os.environ["RECHARGE_API_KEY"]}

recharge_response = requests.get(
    f"{base_url}/api/v1/recharges/stats",
    headers=headers,
    timeout=10,
)
recharge_response.raise_for_status()
recharges = recharge_response.json()["recharges"]

failure_response = requests.get(
    f"{base_url}/api/v1/reports/internet-failures",
    headers=headers,
    timeout=10,
)
failure_response.raise_for_status()
failure_reports = failure_response.json()["reports"]

for report in failure_reports:
    print(report["report_id"], report["status"], report["failure_type"])
```

Para un bot desplegado en otro equipo, `RECHARGE_API_URL` debe apuntar a una
dirección alcanzable por ese equipo. No expongas el servidor de demostración a
Internet sin HTTPS, autenticación y controles de acceso adecuados. El endpoint
de recargas devuelve todos los registros y actualmente no implementa
paginación; el endpoint de reportes limita la respuesta a los 50 más recientes.

## Persistencia y protección de datos

- `DATABASE_PATH` permite elegir dónde guardar SQLite; si no se define, se usa
  `prepago.db` en el proyecto.
- Los reportes y recargas se mantienen entre reinicios mientras se conserve el
  archivo de base de datos.
- Los endpoints de lectura que devuelven datos de clientes y los endpoints de
  escritura requieren API Key.
- Los MSISDN son datos personales; evita publicar respuestas completas en
  registros del bot o canales no autorizados.

## Pruebas

Desde la carpeta del proyecto:

```powershell
python -m unittest discover -s tests -v
```
