---
title: Pavimentados UNEXPO
emoji: 🛣️
colorFrom: orange
colorTo: red
sdk: gradio
sdk_version: "5.1.0"
app_file: app.py
pinned: false
license: mit
short_description: "Sistema Experto Híbrido de Inspección Vial — UNEXPO Mecatrónica. Aplicación base tomada del repositorio del Banco Interamericano de Desarrollo - BID: https://github.com/EL-BID/pavimentados/tree/main"
---

# 🛣️ Pavimentados UNEXPO

**Pavimentados UNEXPO** es una aplicación neuro-simbólica híbrida de Inteligencia Artificial diseñada como herramienta práctica y caso de estudio educativo para la unidad curricular de **Inteligencia Artificial** en la Universidad Nacional Experimental Politécnica (UNEXPO), Núcleo Guarenas, para la demostración del tema **Sistemas Expertos**.

Esta plataforma integra la **percepción visual** con el **razonamiento lógico simbólico** para inspeccionar pavimentos de carreteras en tiempo real y emitir diagnósticos estructurados de ingeniería civil.

---

## 🏗️ Arquitectura Neuro-Simbólica Híbrida

El sistema combina dos enfoques fundamentales de la Inteligencia Artificial:

1. **IA Conexionista (Capa de Percepción Profunda - YOLOv8)**:
   - Procesa los fotogramas del video para detectar grietas (D00), fatiga en piel de cocodrilo (D10), baches abiertos (D40) y desgaste de señalización horizontal (D43/D44).
   - Genera coordenadas (cajas delimitadoras) y niveles de confianza estadística.

2. **IA Simbólica (Capa Basada en Conocimiento - Motor de Inferencia)**:
   - Traduce las detecciones a Hechos lógicos en la **Memoria de Trabajo**.
   - Ejecuta un motor de **Encadenamiento Hacia Adelante (Forward Chaining)** contra una **Base de Conocimiento** formalizada en archivos YAML independientes.
   - Determina la severidad del daño, el Índice de Condición del Pavimento (ICP) global por tramos viales, y recomienda las acciones físicas de mantenimiento (ej: bacheo profundo, fresado) y su nivel de prioridad técnica (URGENTE, ALTA, MEDIA, BAJA).

---

## 🚀 Características de la Plataforma

- **Pestaña 📹 Análisis de Video**: Sube videos de carreteras viales, ajusta la frecuencia de muestreo de fotogramas, procesa con YOLOv8 y visualiza los frames anotados con HUDs interactivos y una galería de fallas recortadas.
- **Pestaña 🧠 Sistema Experto (Aula Interactiva)**: Explora la **Traza de Razonamiento** secuencial que explica exactamente por qué el sistema tomó sus decisiones (Explicabilidad). Cuenta con un **Editor de Reglas YAML** para modificar umbrales o prioridades en caliente y re-evaluar la calzada en 50 milisegundos.
- **Pestaña 📊 Resultados y Métricas**: Dashboard analítico con tablas descriptivas y gráficos de barras Matplotlib de distribución de fallas. Permite exportar y descargar reportes técnicos completos en español.

---

## 💻 Ejecución Local

Para correr el proyecto en computadoras locales o servidores de la UNEXPO:

1. **Instalar dependencias**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Unpack de Modelos**:
   Asegúrate de que los pesos de YOLOv8 estén extraídos en `modelos/artifacts/`.

3. **Lanzar la aplicación**:
   ```bash
   python app.py
   ```

4. **Acceso web**:
   Ingresa a `http://localhost:7860` en tu navegador web.

**Creado por:** prof. Mónica Tahan como parte del contenido académico para la enseñanza de Inteligencia Artificial en la Unexpo Guarenas, demostrando también el uso del vibe coding y los modelos del agente **Google Antigravity** - Mayo, 2026