---
title: Unexpo Video Translator
emoji: 🎓
colorFrom: blue
colorTo: indigo
sdk: gradio
app_file: app.py
pinned: false
---

# 🎓 AI Video Dubber - Proyecto Universitario (UNEXPO NÚCLEO GUARENAS. ING. MECATRÓNICA)

Este repositorio es una solución integral para la traducción y doblaje automático de contenidos educativos del inglés al español, diseñada específicamente para entornos con recursos de hardware limitados (como universidades públicas).

El proyecto ofrece una **Arquitectura Dual**:
1.  **Local Rápido**: Ejecución inmediata en laptops modestas usando algoritmos de visión por computadora clásicos.
2.  **Cloud Generativo**: Una aplicación lista para desplegar en **Hugging Face Spaces** que realiza el trabajo pesado con IA fotorrealista.

---

## 📂 Anatomía del Proyecto

Para que entiendas cómo funciona el "motor" detrás de este software, aquí tienes la descripción de sus piezas:

### ⚙️ Módulos del Sistema (Backend)
- `transcription.py`: Convierte el audio original en texto usando IA.
- `translation.py`: Traduce los subtítulos detectados al idioma destino.
- `tts.py`: Genera una nueva voz (Text-to-Speech) que suena natural.
- `audio_utils.py`: Herramientas para extraer, mezclar y sincronizar el audio con el video.

### 🚀 Aplicaciones Principales
- `main.py`: Es la aplicación local. Ejecuta todo el proceso y usa `mediapipe_lipsync.py` para mover los labios rápidamente sin calentar el computador.
- `app.py`: El archivo maestro para huggin face spaces

---

## 🛠️ Instalación Local

1.  **Requisitos**: Python 3.8+ y FFmpeg instalado.
    - *Tip*: En Windows, puedes ejecutar `install_ffmpeg.ps1` como Administrador para instalarlo automáticamente.

2.  **Configurar entorno**:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Ejecutar**:
    ```bash
    # Por defecto traduce a español ('es')
    python main.py --input tu_video.mp4
    
    # Para traducir a italiano, francés, etc.
    python main.py --input tu_video.mp4 --target it
    ```

---

## 🌍 Soporte Multilingüe

El sistema soporta actualmente los siguientes idiomas destino (tanto en local como en la nube):
- **es**: Español (Álvaro)
- **it**: Italiano (Diego)
- **fr**: Francés (Henri)
- **de**: Alemán (Conrad)
- **pt**: Portugués (Duarte)
- **ja**: Japonés (Keita)
- **zh**: Chino (Yunxi)

---



### Desarrollado para fines educativos de la asignatura Inteligencia Artificial en la Unexpo Guarenas. Carrera de Ingeniería Mecatrónica. 🏛️✨
### Autor: Profesora Mónica Tahan con el uso de Google Antigravity

