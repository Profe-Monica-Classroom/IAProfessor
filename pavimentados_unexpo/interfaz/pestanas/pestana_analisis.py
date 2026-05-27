# -*- coding: utf-8 -*-
"""
Pestaña de Análisis de Video — Pavimentados UNEXPO.
Maneja la interfaz de carga de videos viales, parametrización de FPS de muestreo,
activación de modelos y visualización de resultados y recortes en tiempo real.
"""

import os
import gradio as gr
from pathlib import Path

def crear_pestana_analisis(procesador):
    """
    Construye la Pestaña 1: Análisis de Video de la app Gradio.
    Retorna los componentes clave para enlazar eventos.
    """
    with gr.Row():
        with gr.Column(scale=1, elem_classes="glass-card"):
            gr.Markdown("### 📹 Carga y Configuración del Video")
            gr.Markdown("Sube un video de inspección vial para procesarlo con los modelos de Inteligencia Artificial (YOLOv8) y el Sistema Experto.")
            
            # Selector de archivo (gr.File evita la necesidad de FFmpeg en el cliente durante la carga)
            input_video = gr.File(label="Subir Archivo de Video Vial", file_types=[".mp4", ".avi", ".mov", ".mkv"])
            
            # Controles
            with gr.Group():
                gr.Markdown("**⚙️ Parámetros de Procesamiento**")
                
                slider_fps = gr.Slider(
                    minimum=1, maximum=5, value=2, step=1, 
                    label="Tasa de Muestreo (Frames por segundo - FPS)", 
                    info="Valores menores aceleran el procesamiento significativamente en CPU."
                )
                
                slider_seccion = gr.Slider(
                    minimum=5, maximum=30, value=10, step=5, 
                    label="Duración de Sección (Segundos)", 
                    info="Cada tramo virtual de tiempo equivale a una sección vial de 100 metros."
                )
                
                check_senales = gr.Checkbox(
                    label="Habilitar Detección de Señales de Tránsito", 
                    value=False, 
                    info="Usa el modelo YOLO v11 adicional para identificar carteles."
                )
                
            btn_analizar = gr.Button("▶️ Iniciar Análisis Vial", elem_classes="btn-primary")
            
        with gr.Column(scale=1):
            with gr.Column(elem_classes="glass-card"):
                gr.Markdown("### 🎬 Calzada Anotada (Resultado con HUD)")
                output_video = gr.Video(label="Video Analizado con HUD y Cajas de Fallas", interactive=False)
                
            with gr.Column(elem_classes="glass-card"):
                gr.Markdown("### 🖼️ Galería de Fallas Detectadas")
                gr.Markdown("Haz clic en cualquier imagen para ampliar y auditar el código de falla catalogado.")
                output_galeria = gr.Gallery(
                    label="Recortes de Daños Viales", 
                    columns=4, 
                    rows=2, 
                    height="auto",
                    preview=True,
                    object_fit="contain"
                )
                
    return input_video, slider_fps, slider_seccion, check_senales, btn_analizar, output_video, output_galeria
