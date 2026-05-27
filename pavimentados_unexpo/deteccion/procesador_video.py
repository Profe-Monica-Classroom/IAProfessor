# -*- coding: utf-8 -*-
"""
Pavement Video Processor — Pavimentados UNEXPO.
Implements the core video processing pipeline. Reads frames, performs YOLOv8/v11
deep learning inferences, translates detections into logical expert system Facts,
triggers the forward-chaining rules engine per section to determine pavement condition (PCI),
and outputs the final annotated video with an integrated HUD overlay.
"""

import os
import sys
import cv2
import numpy as np
import pandas as pd
from pathlib import Path

# Add package root to sys.path to ensure consistent absolute imports
PACKAGE_ROOT = Path(__file__).resolve().parent.parent
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

# Dynamically add the original Pavimentados project source directory to path
ORIGINAL_PROJECT_ROOT = PACKAGE_ROOT.parent
RUTA_PAVIMENTADOS_ORIGINAL = ORIGINAL_PROJECT_ROOT / "pavimentados-main"
if str(RUTA_PAVIMENTADOS_ORIGINAL) not in sys.path:
    sys.path.append(str(RUTA_PAVIMENTADOS_ORIGINAL))

# Import expert system core and UNEXPO visualizer with absolute paths
from sistema_experto.memoria_trabajo import Hecho, MemoriaTrabajo
from sistema_experto.base_conocimiento import cargar_reglas_desde_yaml
from sistema_experto.motor import MotorInferencia
from sistema_experto.traza_razonamiento import TrazaRazonamiento
from deteccion.clasificador_fallas import traducir_detecciones_a_hechos, NOMBRES_CLASES_ESPANOL, MAPEO_CLASES_PAVIMENTO
from deteccion.visualizador import dibujar_cajas, dibujar_hud_seccion, recortar_y_guardar_falla, generar_grafico_distribucion_fallas


# Import original YOLOv8 wrapper
try:
    from pavimentados.models.yolov8 import YoloV8Model
except ImportError as e:
    print(f"Warning importing original Pavimentados modules: {e}")

# Default YOLOv8 models configuration
CONFIG_MODELOS = {
    "general_path": str(PACKAGE_ROOT / "modelos" / "artifacts"),
    "paviment_model": {
        "enabled": True,
        "path": "paviment_model/yolov8-road-damage-old-classes-240724-1800",
        "model_filename": "model.pt",
        "classes_filename": "classes.names",
        "yolo_threshold": 0.15,
        "yolo_iou": 0.45,
        "yolo_max_detections": 100,
        "classes_codes_to_exclude": ["OT0"]
    },
    "signal_model": {
        "enabled": False,  # Disabled by default to accelerate CPU runs in classroom demo, configurable
        "path": "signal_model/yolo11-signals-datasetWOotherysem-250115-2342",
        "model_filename": "model.pt",
        "classes_filename": "classes.names",
        "yolo_threshold": 0.20,
        "yolo_iou": 0.45,
        "yolo_max_detections": 50
    }
}

class ProcesadorVideoUNEXPO:
    def __init__(self, habilitar_senales: bool = False, device: str = "cpu"):
        self.habilitar_senales = habilitar_senales
        self.device = device
        self.config = CONFIG_MODELOS.copy()
        self.config["signal_model"]["enabled"] = habilitar_senales
        
        # Application directory paths
        self.ruta_modelos = PACKAGE_ROOT / "modelos" / "artifacts"
        self.ruta_reglas = PACKAGE_ROOT / "sistema_experto" / "reglas"
        self.ruta_recortes = PACKAGE_ROOT / "ejemplos" / "recortes_fallas"
        
        os.makedirs(self.ruta_recortes, exist_ok=True)
        
        # Load all expert system rules
        self.reglas = []
        for r_name in ["reglas_severidad.yaml", "reglas_condicion.yaml", "reglas_mantenimiento.yaml", "reglas_seguridad.yaml"]:
            self.reglas.extend(cargar_reglas_desde_yaml(str(self.ruta_reglas / r_name)))
            
        self.motor = MotorInferencia(self.reglas)
        self.modelos_cargados = False

    def cargar_modelos(self):
        """Initializes and loads YOLO deep learning model weights."""
        if self.modelos_cargados:
            return
            
        print("📥 Loading Deep Learning models...")
        self.yolo_pavimento = YoloV8Model(
            config=self.config,
            device=self.device,
            model_config_key="paviment_model",
            artifacts_path=str(self.ruta_modelos)
        )
        
        if self.habilitar_senales:
            self.yolo_senales = YoloV8Model(
                config=self.config,
                device=self.device,
                model_config_key="signal_model",
                artifacts_path=str(self.ruta_modelos)
            )
        else:
            self.yolo_senales = None
            
        self.modelos_cargados = True
        print("✅ Models loaded successfully.")

    def procesar_video(self, ruta_video: str, fps_muestreo: int = 2, 
                       segundos_por_seccion: int = 10, progreso_callback=None) -> dict:
        """
        Executes the complete video processing pipeline.
        - Stage 1: Run YOLOv8 object detection on sampled frames.
        - Stage 2: Translate raw boxes into Facts and run the Expert System.
        - Stage 3: Render the final annotated video with bounding boxes and HUD panels.
        
        progreso_callback: Gradio-compatible callback function f(fraction, text) to report status.
        """
        # Ensure models are loaded
        self.cargar_modelos()
        
        # Clear previous defect crops
        for f in os.listdir(self.ruta_recortes):
            if f.endswith((".png", ".jpg")):
                try:
                    os.remove(self.ruta_recortes / f)
                except:
                    pass
                    
        cap = cv2.VideoCapture(ruta_video)
        if not cap.isOpened():
            raise FileNotFoundError(f"Could not open video file at {ruta_video}")
            
        fps_video = cap.get(cv2.CAP_PROP_FPS)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        ancho = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        alto = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        duracion = total_frames / fps_video if fps_video else 0
        
        print(f"🎬 Loaded video: {total_frames} frames, {fps_video} FPS, {duracion:.1f} seconds.")
        
        # Frame sampling interval
        intervalo_frames = max(1, int(fps_video // fps_muestreo))
        frames_a_procesar = list(range(0, total_frames, intervalo_frames))
        
        # Stage 1: Deep Learning Perception (YOLOv8)
        detecciones_individuales = []  # List of dicts containing raw detections
        frames_guardados = {}  # {frame_idx: frame_rgb} cache for rendering
        
        for num_p, frame_idx in enumerate(frames_a_procesar):
            if progreso_callback:
                progreso_callback(num_p / len(frames_a_procesar) * 0.45, 
                                  f"Analyzing frame {frame_idx}/{total_frames} (Deep Learning)...")
                                  
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frames_guardados[frame_idx] = frame_rgb
            
            # Map frame index to section ID based on segment duration
            tiempo_seg = frame_idx / fps_video
            seccion_id = int(tiempo_seg // segundos_por_seccion) + 1
            
            # Run pavement defect detection
            boxes_pav, scores_pav, classes_pav = self.yolo_pavimento.predict(np.expand_dims(frame_rgb, axis=0))
            
            # Process pavement detections
            for box, score, clase in zip(boxes_pav[0], scores_pav[0], classes_pav[0]):
                tipo_cod = MAPEO_CLASES_PAVIMENTO.get(clase, "OT0")
                detecciones_individuales.append({
                    "frame_idx": frame_idx,
                    "seccion": seccion_id,
                    "clase_idx": clase,
                    "tipo_falla": tipo_cod,
                    "nombre_falla": NOMBRES_CLASES_ESPANOL.get(tipo_cod, "Falla"),
                    "confianza": score,
                    "boxes": box,  # [x1, y1, x2, y2]
                    "area": (box[2] - box[0]) * (box[3] - box[1]) * ancho * alto
                })
                
            # Run traffic signal detection (optional)
            if self.habilitar_senales and self.yolo_senales:
                boxes_sig, scores_sig, classes_sig = self.yolo_senales.predict(np.expand_dims(frame_rgb, axis=0))
                for box, score, clase in zip(boxes_sig[0], scores_sig[0], classes_sig[0]):
                    # Classify as SIGN
                    nombre_sen = self.yolo_senales.classes_idx_names.get(clase, "Senal Vial")
                    detecciones_individuales.append({
                        "frame_idx": frame_idx,
                        "seccion": seccion_id,
                        "clase_idx": -1,  # Signal marker
                        "tipo_falla": "SIGN",
                        "nombre_falla": f"Senal: {nombre_sen}",
                        "confianza": score,
                        "boxes": box,
                        "area": (box[2] - box[0]) * (box[3] - box[1]) * ancho * alto
                    })
                    
        cap.release()
        
        # Stage 2: Symbolic Reasoning (Expert System)
        if progreso_callback:
            progreso_callback(0.50, "Executing Expert System Inferences...")
            
        # Translate raw YOLO detections into Spanish Facts
        hechos_ind, hechos_sec = traducir_detecciones_a_hechos(detecciones_individuales)
        
        # Group Facts by section to execute inference engine segment by segment
        hechos_por_seccion = {}  # {seccion_id: [facts]}
        for h in hechos_ind:
            sec = h.obtener("seccion")
            hechos_por_seccion.setdefault(sec, []).append(h)
            
        for hs in hechos_sec:
            sec = hs.obtener("seccion")
            hechos_por_seccion.setdefault(sec, []).append(hs)
            
        # Run the Inference Engine per road section
        conclusiones_secciones = {}  # {seccion_id: {condicion_via, prioridad_obra, riesgo_seguridad, traza_md}}
        
        for seccion_id, hechos_sec_lista in hechos_por_seccion.items():
            memoria = MemoriaTrabajo()
            for h in hechos_sec_lista:
                memoria.agregar(h)
                
            traza = TrazaRazonamiento()
            self.motor.inferir(memoria, traza)
            
            # Extract derived conclusions for HUD overlay and reports
            cond_via = "EXCELENTE"
            prio_obra = "NINGUNA"
            riesgo = "BAJO"
            
            conds = memoria.obtener_por_nombre("condicion_via")
            if conds:
                cond_via = conds[0].obtener("indice")
                
            mants = memoria.obtener_por_nombre("mantenimiento")
            if mants:
                prio_obra = mants[0].obtener("prioridad")
                
            riesgos = memoria.obtener_por_nombre("riesgo_seguridad")
            if riesgos:
                riesgo = riesgos[0].obtener("nivel")
                
            conclusiones_secciones[seccion_id] = {
                "condicion": cond_via,
                "prioridad": prio_obra,
                "riesgo": riesgo,
                "traza": traza.formatear_markdown(seccion_id=seccion_id)
            }
            
            # Copy derived conclusions to the global facts list for the report generator
            for c_hecho in memoria.hechos:
                if c_hecho not in hechos_ind and c_hecho not in hechos_sec:
                    hechos_ind.append(c_hecho)
                    
        # Stage 3: Render and Save the Annotated Video (HUD + Bounding Boxes)
        if progreso_callback:
            progreso_callback(0.60, "Rendering final annotated video...")
            
        ruta_video_anotado = str(ORIGINAL_PROJECT_ROOT / "pavimentados_unexpo" / "ejemplos" / "analisis_salida.mp4")
        
        # Try utilizing H.264 (avc1) for direct browser HTML5 playback compatibility
        fourcc = cv2.VideoWriter_fourcc(*"avc1")
        out_video = cv2.VideoWriter(ruta_video_anotado, fourcc, fps_muestreo, (ancho, alto))
        
        if not out_video.isOpened():
            # Fallback to standard mp4v if avc1 driver is missing in the host system
            print("Warning: Could not initialize avc1 (H.264) codec. Falling back to mp4v.")
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out_video = cv2.VideoWriter(ruta_video_anotado, fourcc, fps_muestreo, (ancho, alto))
        
        # Track saved crops to avoid duplicating images in the interactive Gradio gallery
        recortes_vistos = set()
        
        for num_p, frame_idx in enumerate(frames_a_procesar):
            if progreso_callback:
                progreso_callback(0.60 + (num_p / len(frames_a_procesar) * 0.35), 
                                  f"Writing annotated frame {frame_idx}...")
                                  
            frame_rgb = frames_guardados.get(frame_idx)
            if frame_rgb is None:
                continue
                
            # Filter detections for the current frame
            dets_frame = [d for d in detecciones_individuales if d["frame_idx"] == frame_idx]
            
            # Draw color-coded bounding boxes
            frame_dibujado = dibujar_cajas(frame_rgb, dets_frame)
            
            # Retrieve segment ID and its logical expert system conclusions
            tiempo_seg = frame_idx / fps_video
            seccion_id = int(tiempo_seg // segundos_por_seccion) + 1
            concl = conclusiones_secciones.get(seccion_id, {
                "condicion": "EXCELENTE",
                "prioridad": "NINGUNA",
                "riesgo": "BAJO"
            })
            
            # Draw overlay HUD panel
            frame_dibujado = dibujar_hud_seccion(
                frame_dibujado,
                seccion_actual=seccion_id,
                total_fallas_seccion=len([d for d in detecciones_individuales if d["seccion"] == seccion_id]),
                condicion_seccion=concl["condicion"],
                prioridad_seccion=concl["prioridad"]
            )
            
            # Save cropped defect images for interactive audit in the gallery
            for d in dets_frame:
                id_falla = d["id_falla"]
                if id_falla not in recortes_vistos:
                    recortes_vistos.add(id_falla)
                    ruta_recorte = str(self.ruta_recortes / f"{id_falla}_{d['tipo_falla']}.jpg")
                    recortar_y_guardar_falla(frame_rgb, d["boxes"], ruta_recorte)
                    
            # Convert RGB (Gradio/YOLO default) to BGR (required by OpenCV VideoWriter)
            frame_bgr = cv2.cvtColor(frame_dibujado, cv2.COLOR_RGB2BGR)
            out_video.write(frame_bgr)
            
        out_video.release()
        
        # Generate final distribution chart for the Results Dashboard tab
        ruta_grafico = str(ORIGINAL_PROJECT_ROOT / "pavimentados_unexpo" / "ejemplos" / "grafico_fallas.png")
        generar_grafico_distribucion_fallas(hechos_ind, ruta_grafico)
        
        # Compile summary stats per road section
        resumen_secciones = []
        for s_id, concl in conclusiones_secciones.items():
            num_f = len([d for d in detecciones_individuales if d["seccion"] == s_id and d.get("clase_idx", -1) >= 0])
            num_b = len([d for d in detecciones_individuales if d["seccion"] == s_id and d.get("tipo_falla") == "D40"])
            resumen_secciones.append({
                "Sección": s_id,
                "Total Fallas": num_f,
                "Baches": num_b,
                "Condición (ICP)": concl["condicion"],
                "Prioridad Obra": concl["prioridad"],
                "Nivel Riesgo": concl["riesgo"]
            })
            
        df_resumen = pd.DataFrame(resumen_secciones)
        
        if progreso_callback:
            progreso_callback(1.0, "Processing complete!")
            
        return {
            "video_anotado": ruta_video_anotado,
            "grafico_fallas": ruta_grafico,
            "tabla_resumen": df_resumen,
            "hechos": hechos_ind,
            "trazas": conclusiones_secciones,
            "recortes_directorio": str(self.ruta_recortes)
        }
