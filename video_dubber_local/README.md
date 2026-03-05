# 🎙️ Video Dubber Local - UNEXPO Núcleo Guarenas. Asignatura IA. Prof. Mónica Tahan. mtahan@unexpo.edu.ve (Bilingual Version)

[Español](#español) | [English](#english)

---

<a name="español"></a>
## 🇪🇸 Versión en Español

Este proyecto permite realizar el doblaje automático de videos (Inglés -> Otros Idiomas) utilizando Inteligencia Artificial. Está diseñado como una herramienta educativa para las clases de IA de la UNEXPO, con soporte para diferentes arquitecturas de hardware.

### 🚀 Modos de Ejecución (Seleccionando la Calidad)

El script detecta y permite elegir el motor de Lip Sync (sincronización de labios) según su hardware:

1.  **Modo Inteligente Intel (Acelerado por OpenVINO)**: creado con openvino para procesadores Intel modernos (Core Ultra/Iris Xe). Usa la NPU y GPU integrada para alta calidad local.
    ```powershell
    python main.py video.mp4 --quality intel
    ```
2.  **Modo NVIDIA / CUDA (Alta Calidad Estándar)**: Emplea la configuración nativa de wav2lip para tarjetas NVIDIA. **Wav2Lip**.
    ```powershell
    python main.py video.mp4 --quality high
    ```
3.  **Modo Básico / Rápido (Universal)**: Funciona en cualquier PC. Utiliza visión clásica y deformación matemática para el movimiento de la boca. Aquí vas a notar como se deforma la zona de la boca en el video final.
    ```powershell
    python main.py video.mp4 --quality fast
    ```
4.  **Modo Híbrido (Nube)**: Delega el trabajo pesado a Hugging Face a través de la API, para evitar problemas de hardware.
    ```powershell
    python main.py video.mp4 --quality cloud
    ```

### 🛠️ Instalación y Requisitos
*   **Python 3.10 - 3.13**
*   **FFmpeg**: Obligatorio. (Usa `install_ffmpeg.ps1`).
*   **Comando de instalación**: `pip install -r requirements.txt`

---

<a name="english"></a>
## 🇺🇸 English Version

This project enables automatic video dubbing (English -> Other Languages) using Artificial Intelligence. It is designed as an educational tool for AI classes at UNEXPO, with support for different hardware architectures.

### 🚀 Execution Modes (Quality Selection)

The script allows you to choose the Lip Sync engine based on your available hardware:

1.  **Intel Smart Mode (OpenVINO Accelerated)**: Optimized for modern Intel processors (Core Ultra/Iris Xe). Uses the integrated NPU and GPU for high-quality local processing.
    ```powershell
    python main.py video.mp4 --quality intel
    ```
2.  **NVIDIA / CUDA Mode (Standard High Quality)**: Use this mode if you have a dedicated NVIDIA graphics card in your computer. Uses the **Wav2Lip** implementation.
    ```powershell
    python main.py video.mp4 --quality high
    ```
3.  **Basic / Fast Mode (Universal)**: Works on any PC. Uses classical vision and mathematical warping for mouth movement. Here you will notice how the mouth area deforms in the final video.
    ```powershell
    python main.py video.mp4 --quality fast
    ```
4.  **Hybrid Mode (Cloud)**: Offloads the heavy processing to Hugging Face via API, to avoid hardware issues.
    ```powershell
    python main.py video.mp4 --quality cloud
    ```

### 🛠️ Installation & Requirements
*   **Python 3.10 - 3.13**
*   **FFmpeg**: Required. (Use `install_ffmpeg.ps1`).
*   **Installation command**: `pip install -r requirements.txt`

---

## 🏛️ Créditos / Credits
Desarrollado para la **Universidad Nacional Experimental Politécnica (UNEXPO Núcleo Guarenas), asignatura IA. Profesora: Mónica Tahan (mtahan@unexpo.edu.ve). empleando  Google Antigravity**. 
Developed for the **National Experimental Polytechnic University (UNEXPO Núcleo Guarenas), AI subject. Professor: Mónica Tahan (mtahan@unexpo.edu.ve). Using Google Antigravity**.
