# -*- coding: utf-8 -*-
"""
Results Visualizer — Pavimentados UNEXPO.
Handles video bounding box overlay rendering, real-time telemetry HUD panel superimposition,
defect cropping for the interactive Gradio gallery, and matplotlib statistical charts compilation.
"""

import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
from pathlib import Path

# Import Spanish human-readable class names for the final output charts
try:
    from deteccion.clasificador_fallas import NOMBRES_CLASES_ESPANOL
except ImportError:
    try:
        from clasificador_fallas import NOMBRES_CLASES_ESPANOL
    except ImportError:
        NOMBRES_CLASES_ESPANOL = {
            "D00": "Grieta Longitudinal/Transversal",
            "D10": "Grieta en Piel de Cocodrilo",
            "D40": "Bache o Hundimiento Abierto",
            "D43": "Desgaste de Paso Peatonal",
            "D44": "Desgaste de Línea de Carril",
            "OT0": "Otros Daños Menores"
        }

# Harmonized BGR color palette (OpenCV uses BGR format natively)
COLORES_BGR = {
    "D00": (0, 255, 255),    # Linear Cracks: Yellow
    "D10": (0, 140, 255),    # Alligator Cracking: Orange
    "D40": (0, 0, 255),      # Open Pothole: Bright Red
    "D43": (255, 128, 0),    # Crosswalks: Light Blue
    "D44": (255, 0, 128),    # Lane Lines: Pink
    "OT0": (128, 128, 128),  # Others: Gray
    "SIGN": (0, 255, 0)      # Traffic Signals: Green
}

def obtener_color(tipo_falla: str) -> tuple[int, int, int]:
    """Returns the corresponding BGR color tuple for a standardized defect code."""
    return COLORES_BGR.get(tipo_falla, (255, 255, 255))

def dibujar_cajas(frame: np.ndarray, detecciones: list[dict]) -> np.ndarray:
    """
    Draws bounding boxes and Spanish human-readable tags over a video frame.
    """
    img = frame.copy()
    h_img, w_img = img.shape[:2]
    
    for det in detecciones:
        boxes = det["boxes"]  # [x1, y1, x2, y2] normalized
        tipo = det["tipo_falla"]
        nombre = det["nombre_falla"]
        conf = det["confianza"]
        id_falla = det["id_falla"]
        
        # Denormalize coordinates to match image dimensions
        x1 = int(boxes[0] * w_img)
        y1 = int(boxes[1] * h_img)
        x2 = int(boxes[2] * w_img)
        y2 = int(boxes[3] * h_img)
        
        color = obtener_color(tipo)
        
        # Draw main rectangle
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        
        # Tag text format
        texto = f"{id_falla}: {nombre} ({conf:.0%})"
        
        # Determine tag position and draw a filled background card for readability
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.4
        thickness = 1
        (w_txt, h_txt), baseline = cv2.getTextSize(texto, font, scale, thickness)
        
        y_txt = y1 - 8 if y1 - 8 > h_txt else y1 + h_txt + 8
        cv2.rectangle(img, (x1, y_txt - h_txt - 4), (x1 + w_txt + 6, y_txt + baseline), color, cv2.FILLED)
        cv2.putText(img, texto, (x1 + 3, y_txt - 2), font, scale, (255, 255, 255), thickness, cv2.LINE_AA)
        
    return img

def dibujar_hud_seccion(frame: np.ndarray, seccion_actual: int, 
                        total_fallas_seccion: int, condicion_seccion: str = "Plausi.",
                        prioridad_seccion: str = "Calculando...") -> np.ndarray:
    """
    Draws a translucent, high-end telemetry HUD panel in the top-left corner
    representing professional mechatronics dashboard visualizers.
    """
    img = frame.copy()
    h_img, w_img = img.shape[:2]
    
    # HUD panel dimension setup
    ancho_hud = 280
    alto_hud = 110
    pad = 15
    
    # Create translucent overlay
    overlay = img.copy()
    cv2.rectangle(overlay, (pad, pad), (pad + ancho_hud, pad + alto_hud), (18, 18, 18), cv2.FILLED)
    
    # Apply alpha blending (alpha = 0.75)
    cv2.addWeighted(overlay, 0.75, img, 0.25, 0, img)
    
    # Draw fine border in amber/gold color
    cv2.rectangle(img, (pad, pad), (pad + ancho_hud, pad + alto_hud), (0, 165, 255), 1)
    
    # Draw text annotations in the HUD
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, "🛣️ PAVIMENTADOS UNEXPO", (pad + 12, pad + 22), font, 0.45, (0, 165, 255), 1, cv2.LINE_AA)
    cv2.putText(img, "-" * 32, (pad + 12, pad + 32), font, 0.4, (120, 120, 120), 1, cv2.LINE_AA)
    
    cv2.putText(img, f"Tramo Vial Actual : Seccion {seccion_actual}", (pad + 12, pad + 48), font, 0.4, (240, 240, 240), 1, cv2.LINE_AA)
    cv2.putText(img, f"Fallas en Seccion : {total_fallas_seccion} detectadas", (pad + 12, pad + 66), font, 0.4, (240, 240, 240), 1, cv2.LINE_AA)
    
    # Color-code condition text according to PCI index levels
    color_icp = (255, 255, 255)
    if condicion_seccion == "EXCELENTE":
        color_icp = (0, 255, 0)
    elif condicion_seccion == "BUENO":
        color_icp = (255, 255, 0)
    elif condicion_seccion == "REGULAR":
        color_icp = (0, 255, 255)
    elif condicion_seccion in ["MALO", "MUY_MALO"]:
        color_icp = (0, 0, 255)
        
    cv2.putText(img, f"Condicion (ICP)   : ", (pad + 12, pad + 84), font, 0.4, (240, 240, 240), 1, cv2.LINE_AA)
    cv2.putText(img, f"{condicion_seccion}", (pad + 120, pad + 84), font, 0.4, color_icp, 1, cv2.LINE_AA)
    cv2.putText(img, f"Prioridad Obra    : {prioridad_seccion}", (pad + 12, pad + 100), font, 0.4, (240, 240, 240), 1, cv2.LINE_AA)
    
    return img

def recortar_y_guardar_falla(frame: np.ndarray, boxes: list[float], 
                             ruta_salida: str, padding: int = 15) -> bool:
    """
    Crops a defect area out of a video frame applying a safety margin padding
    and saves it to disk for the interactive Gradio gallery view.
    """
    h_img, w_img = frame.shape[:2]
    
    # Denormalize coordinates
    x1 = int(boxes[0] * w_img)
    y1 = int(boxes[1] * h_img)
    x2 = int(boxes[2] * w_img)
    y2 = int(boxes[3] * h_img)
    
    # Apply safety padding margins
    x1 = max(0, x1 - padding)
    y1 = max(0, y1 - padding)
    x2 = min(w_img, x2 + padding)
    y2 = min(h_img, y2 + padding)
    
    try:
        recorte = frame[y1:y2, x1:x2]
        if recorte.size > 0:
            # Convert RGB frame cache back to BGR for standard cv2.imwrite output
            recorte_bgr = cv2.cvtColor(recorte, cv2.COLOR_RGB2BGR)
            cv2.imwrite(ruta_salida, recorte_bgr)
            return True
    except Exception as e:
        print(f"Error cropping road defect: {e}")
        
    return False

def generar_grafico_distribucion_fallas(hechos_individuales: list, ruta_grafico: str) -> bool:
    """
    Generates a horizontal bar chart displaying defect distributions by category using Matplotlib
    and saves it to disk for rendering in the Gradio dashboard tab.
    """
    conteos = {"D00": 0, "D10": 0, "D40": 0, "D43": 0, "D44": 0, "OT0": 0}
    
    for h in hechos_individuales:
        tipo = h.obtener("tipo_falla")
        if tipo in conteos:
            conteos[tipo] += 1
            
    etiquetas = [NOMBRES_CLASES_ESPANOL.get(k, k) for k in conteos.keys()]
    valores = list(conteos.values())
    
    # Filter out categories with zero detections to improve readability
    elementos = [(et, val) for et, val in zip(etiquetas, valores) if val > 0]
    if not elementos:
        return False
        
    etiquetas_filtradas, valores_filtrados = zip(*elementos)
    
    plt.figure(figsize=(8, 4), facecolor='#121212')
    ax = plt.subplot(111)
    ax.set_facecolor('#121212')
    
    colores_plot = ['#ffcc00', '#ff8800', '#ff3333', '#33a2ff', '#e033ff', '#999999']
    
    bars = ax.barh(etiquetas_filtradas, valores_filtrados, color=colores_plot[:len(valores_filtrados)])
    
    ax.spines['bottom'].set_color('#444444')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color('#444444')
    ax.tick_params(colors='white')
    ax.xaxis.grid(True, color='#222222', linestyle='--')
    
    plt.title("Distribución de Fallas Viales Detectadas", color='white', fontsize=12, pad=15)
    plt.xlabel("Cantidad de Detecciones", color='white', fontsize=10)
    
    # Add labels on top of the bars
    for bar in bars:
        width = bar.get_width()
        ax.text(width + 0.1, bar.get_y() + bar.get_height()/2, f'{int(width)}', 
                ha='left', va='center', color='white', fontweight='bold')
                
    plt.tight_layout()
    os.makedirs(os.path.dirname(ruta_grafico), exist_ok=True)
    plt.savefig(ruta_grafico, dpi=300, facecolor='#121212')
    plt.close()
    return True
