# -*- coding: utf-8 -*-
"""
Road Defect Classifier and Integrator — Pavimentados UNEXPO.
Translates raw deep learning detections (YOLOv8/v11) into expert system Facts
and consolidates pavement section metrics.
"""
import sys
from pathlib import Path

# Add package root to sys.path to ensure consistent absolute imports
PACKAGE_ROOT = Path(__file__).resolve().parent.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from sistema_experto.memoria_trabajo import Hecho


# Mapping of YOLOv8 pavement class indexes to standardized defect codes
MAPEO_CLASES_PAVIMENTO = {
    0: "D00",  # Longitudinal Linear Crack
    1: "D00",  # Longitudinal Linear Crack Interval -> D00
    2: "D00",  # Transverse Linear Crack -> D00
    3: "D00",  # Transverse Linear Crack Interval -> D00
    4: "D10",  # Alligator Cracking (Piel de Cocodrilo)
    5: "D40",  # Pothole or Open Depressed Area
    6: "D43",  # Pedestrian Crossing Marking wear
    7: "D44",  # Lane Marking Line wear
    8: "OT0"   # Other Minor Defects
}

# Human-readable Spanish descriptions for each standardized defect code (used in final UI reports)
NOMBRES_CLASES_ESPANOL = {
    "D00": "Grieta Longitudinal/Transversal",
    "D10": "Grieta en Piel de Cocodrilo",
    "D40": "Bache o Hundimiento Abierto",
    "D43": "Desgaste de Paso Peatonal",
    "D44": "Desgaste de Línea de Carril",
    "OT0": "Otros Daños Menores"
}

def traducir_detecciones_a_hechos(detecciones_por_frame: list[dict]) -> tuple[list[Hecho], list[Hecho]]:
    """
    Translates a list of frame-by-frame raw deep learning detections into expert system Facts.
    Also aggregates section-level statistics to generate consolidated section Facts (e.g. per 100m virtual segments).
    
    Each individual detection is converted into a Hecho('falla_detectada') Fact.
    Each consolidated section is converted into a Hecho('seccion_analizada') Fact.
    """
    hechos_individuales = []
    secciones_stats = {}  # {seccion_id: {num_fallas, num_baches, ...}}
    
    # 1. Create individual defect Facts and accumulate section-level statistics
    for idx, det in enumerate(detecciones_por_frame):
        id_falla = f"F{idx+1:03d}"
        det["id_falla"] = id_falla  # Write back to prevent KeyError during HUD visualization
        seccion = det.get("seccion", 1)
        clase_idx = det.get("clase_idx")
        confianza = det.get("confianza", 0.0)
        area = det.get("area", 0.0)
        
        # Get standardized code
        tipo_falla = MAPEO_CLASES_PAVIMENTO.get(clase_idx, "OT0")
        
        # Initialize section stats if new
        if seccion not in secciones_stats:
            secciones_stats[seccion] = {
                "num_fallas": 0,
                "num_baches": 0,
                "num_piel_cocodrilo": 0,
                "num_marcas_desgastadas": 0
            }
            
        stats = secciones_stats[seccion]
        stats["num_fallas"] += 1
        
        if tipo_falla == "D40":
            stats["num_baches"] += 1
        elif tipo_falla == "D10":
            stats["num_piel_cocodrilo"] += 1
        elif tipo_falla in ["D43", "D44"]:
            stats["num_marcas_desgastadas"] += 1
            
        # Create individual Hecho (Fact)
        hecho_falla = Hecho(
            "falla_detectada",
            id_falla=id_falla,
            seccion=seccion,
            tipo_falla=tipo_falla,
            area_deteccion=area,
            confianza=confianza,
            nombre_falla=NOMBRES_CLASES_ESPANOL.get(tipo_falla, "Falla Desconocida")
        )
        hechos_individuales.append(hecho_falla)
        
    # 2. Create aggregated section Facts
    hechos_secciones = []
    for seccion_id, stats in secciones_stats.items():
        hecho_seccion = Hecho(
            "seccion_analizada",
            seccion=seccion_id,
            num_fallas=stats["num_fallas"],
            num_baches=stats["num_baches"],
            num_piel_cocodrilo=stats["num_piel_cocodrilo"],
            num_marcas_desgastadas=stats["num_marcas_desgastadas"]
        )
        hechos_secciones.append(hecho_seccion)
        
    return hechos_individuales, hechos_secciones
