Especificación Técnica (SDD): Sistema de Recargas y Dashboard

1. Contexto de Negocio

Como... Gerente de Operaciones de Red Prepago

Quiero... procesar recargas en tiempo real y monitorear la adopción 4G/5G en un dashboard unificado

Para... evitar cobranzas duplicadas, asegurar la estabilidad del servicio y visualizar indicadores que permiten mejorar la toma de decisiones.

2. Requisitos Estructurales (Módulos)

Deberás generar el código para dos componentes aislados que interactúan entre sí:

api.py: Contiene el microservicio transaccional. Además de procesar, debe tener un endpoint GET /api/v1/recharges/stats que devuelva todos los registros para ser leídos por el dashboard.

dashboard.py: Contiene la interfaz analítica en Streamlit que consume los datos de api.py.

3. Especificación del Endpoint Transaccional (api.py)

Método y Ruta: POST /api/v1/recharges/apply

Esquema Pydantic Esperado (RechargeRequest):

msisdn (string)

amount (float): Montos válidos únicamente [50, 100, 200, 500].

network_type (string): Valores válidos únicamente ["4G", "5G"].

location (string)

transaction_id (string): Identificador único.

Criterios de Aceptación (Comportamiento EARS)

SI el transaction_id ya existe en los registros procesados, el sistema debe rechazar la petición con un HTTP 409 Conflict (Prevención de doble cobro).

MIENTRAS el amount o network_type no coincidan con los valores válidos descritos, el sistema debe devolver HTTP 400 Bad Request.

CUANDO el payload sea válido y único, el sistema debe almacenar el registro agregándole un timestamp de la hora actual y devolver HTTP 201 Created.

4. Especificación del Dashboard Analítico (dashboard.py)

Debe ser una interfaz limpia que solicite los datos al endpoint GET y renderice:

KPIs (Tarjetas métricas superiores): Volumen operativo total, Ingreso bruto (suma de montos), y Volumen de adopción 5G.

Gráfico 1 (Pie o Donut): Distribución de ingresos agrupados por monto (50, 100, 200, 500).

Gráfico 2 (Barras): Volumen total de recargas agrupadas por zona/ciudad (location).

5. Requerimientos No Funcionales o Restricciones Técnicas

Arquitectura de Software: El sistema debe estructurarse estrictamente bajo el patrón de diseño MVC (Modelo-Vista-Controlador). 

Debe existir una separación absoluta entre la definición de los datos (SQLite/Modelos), la lógica transaccional de la API (Controlador) y el renderizado del dashboard analítico (Vista).