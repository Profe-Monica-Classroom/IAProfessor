# -*- coding: utf-8 -*-
"""
Main Gradio Application — Pavimentados UNEXPO.
Official entry point that orchestrates the application life cycle, manages global
session states (gr.State), and links UI events across the analysis, expert system,
and results dashboard tabs.
"""

import os
import sys
from pathlib import Path

# Configure local Gradio temp directory to avoid Windows %TEMP% PermissionError
DIRECTORIO_RAIZ = Path(__file__).resolve().parent
TEMP_DIR = DIRECTORIO_RAIZ / "temp"
os.makedirs(TEMP_DIR, exist_ok=True)
os.environ['GRADIO_TEMP_DIR'] = str(TEMP_DIR)

import pandas as pd
import gradio as gr

# Configure UTF-8 on Windows console for proper string rendering
sys.stdout.reconfigure(encoding='utf-8')

# Add relative paths to sys.path
DIRECTORIO_RAIZ = Path(__file__).resolve().parent
sys.path.append(str(DIRECTORIO_RAIZ))

from deteccion.procesador_video import ProcesadorVideoUNEXPO
from deteccion.clasificador_fallas import NOMBRES_CLASES_ESPANOL
from interfaz import CSS_UNEXPO, obtener_tema_gradio
from interfaz import (
    crear_pestana_analisis,
    crear_pestana_experto,
    crear_pestana_resultados
)

# Initialize the UNEXPO global processor (model weights loading is deferred until Analysis is clicked)
procesador_global = ProcesadorVideoUNEXPO(habilitar_senales=False, device="cpu")

def build_app():
    # HTML Banner with academic study case title
    html_banner = """
    <div class="header-unexpo" style="text-align: center; margin-bottom: 20px;">
        <h1 style="margin: 0; font-size: 2.8rem; font-weight: 800;">🛣️ PAVIMENTADOS UNEXPO</h1>
        <p style="margin: 5px 0 0 0; font-size: 1.1rem; color: #a0aec0; letter-spacing: 0.5px;">
            Sistema Experto Híbrido para Inspección de Vialidad y Obras Civiles
        </p>
        <div style="display: inline-block; margin-top: 10px; padding: 4px 12px; background: rgba(255, 152, 0, 0.15); border: 1px solid rgba(255, 152, 0, 0.3); border-radius: 20px;">
            <span style="font-size: 0.85rem; color: #ff9800; font-weight: 600;">🎒 Caso de Estudio: Unidad de Sistemas Expertos y Control Mecatrónico</span>
        </div>
    </div>
    """
    
    with gr.Blocks(
        title="Pavimentados UNEXPO — Sistema Experto"
    ) as demo:
        
        gr.HTML(html_banner)
        
        # Persistent state placeholder to store student session data
        estado_inspeccion = gr.State(value={})
        
        with gr.Tabs() as tabs:
            # Tab 1: Pavement Video Analysis (Deep Learning Perception)
            with gr.Tab("📹 Análisis de Video"):
                (
                    in_video, 
                    fps, 
                    seccion_duracion, 
                    enable_sig, 
                    btn_analizar, 
                    out_video, 
                    out_gallery
                ) = crear_pestana_analisis(procesador_global)
                
            # Tab 2: Symbolic Expert System Reasoning
            with gr.Tab("🧠 Sistema Experto"):
                (
                    dropdown_sec, 
                    out_concl, 
                    out_traza, 
                    btn_reinferir, 
                    sel_yaml, 
                    code_yaml, 
                    btn_save_yaml
                ) = crear_pestana_experto(procesador_global)
                
            # Tab 3: Statistics and Metrics (Dashboard Reports)
            with gr.Tab("📊 Resultados y Métricas"):
                (
                    tabla_metricas, 
                    out_grafico, 
                    out_resumen_ejec, 
                    btn_descarga, 
                    out_file_report
                ) = crear_pestana_resultados(procesador_global)
                

                
        # --- EVENT BINDING AND BUSINESS LOGIC ---
        
        # Event 1: Complete Video Processing Workflow (Deep Learning + Initial Inference Run)
        def ejecutar_analisis_workflow(video_path, fps_muest, segundos_sec, hab_senales, progress=gr.Progress()):
            if not video_path:
                raise gr.Error("Please load a video file first.")
                
            # Configure signal models enabling if toggled
            procesador_global.habilitar_senales = hab_senales
            procesador_global.config["signal_model"]["enabled"] = hab_senales
            
            # Execute main pipeline processing
            resultados = procesador_global.procesar_video(
                ruta_video=video_path,
                fps_muestreo=fps_muest,
                segundos_por_seccion=segundos_sec,
                progreso_callback=progress
            )
            
            # Generate options for the section selection dropdown
            secciones_lista = sorted(list(resultados["trazas"].keys()))
            opciones_dropdown = [str(s) for s in secciones_lista]
            seccion_defecto = opciones_dropdown[0] if opciones_dropdown else "1"
            
            # Retrieve derived conclusions and inference trace for the default section
            concl_def = resultados["trazas"][int(seccion_defecto)]
            conclusiones_texto = (
                f"**Tramo vial**: Sección {seccion_defecto}\n"
                f"- **Condición Estructural (ICP)**: `{concl_def['condicion']}`\n"
                f"- **Nivel de Riesgo**: `{concl_def['riesgo']}`\n"
                f"- **Acción de Obra Recomendada**: `{concl_def['prioridad']}`"
            )
            
            # Compile executive summary markdown
            conteo_baches = sum(1 for h in resultados["hechos"] if h.nombre == "falla_detectada" and h.obtener("tipo_falla") == "D40")
            conteo_fallas = sum(1 for h in resultados["hechos"] if h.nombre == "falla_detectada" and h.obtener("clase_idx", -1) >= 0)
            
            resumen_md = (
                f"**Total Secciones Analizadas**: {len(secciones_lista)} tramos (aprox. {len(secciones_lista)*100} metros viales)\n\n"
                f"**Total Fallas Estructurales**: {conteo_fallas} detecciones catalogadas\n\n"
                f"**Total Baches Abiertos (Riesgo Crítico)**: {conteo_baches} huecos profundos\n\n"
                f"**Condición Vial Promedio**: `{concl_def['condicion']}`"
            )
            
            # Load cropped defect images for interactive viewer
            recortes_archivos = []
            if os.path.exists(resultados["recortes_directorio"]):
                for file_name in os.listdir(resultados["recortes_directorio"]):
                    if file_name.endswith((".jpg", ".png")):
                        partes = file_name.split("_")
                        id_f = partes[0]
                        tipo_f = partes[1].split(".")[0] if len(partes) > 1 else "OT0"
                        lbl = f"{id_f} - {NOMBRES_CLASES_ESPANOL.get(tipo_f, tipo_f)}"
                        recortes_archivos.append((str(Path(resultados["recortes_directorio"]) / file_name), lbl))
            
            return (
                resultados,                                 # gr.State
                resultados["video_anotado"],                # out_video
                recortes_archivos,                          # out_gallery
                gr.Dropdown(choices=opciones_dropdown, value=seccion_defecto), # dropdown_sec
                conclusiones_texto,                         # out_concl
                concl_def["traza"],                         # out_traza
                resultados["tabla_resumen"],                # tabla_metricas
                resultados["grafico_fallas"],               # out_grafico
                resumen_md                                  # out_resumen_ejec
            )
            
        btn_analizar.click(
            fn=ejecutar_analisis_workflow,
            inputs=[in_video, fps, seccion_duracion, enable_sig],
            outputs=[
                estado_inspeccion,
                out_video,
                out_gallery,
                dropdown_sec,
                out_concl,
                out_traza,
                tabla_metricas,
                out_grafico,
                out_resumen_ejec
            ]
        )
        
        # Event 2: Display expert trace and conclusions for a selected section
        def mostrar_conclusiones_seccion(seccion_str, estado):
            if not seccion_str:
                return "*Seleccione una sección en el menú desplegable.*", "*Esperando selección de tramo vial...*"
            if not estado or "trazas" not in estado:
                return "*Suba y analice un video primero.*", "*No hay traza registrada en la memoria.*"
                
            try:
                sec_id = int(seccion_str)
            except (ValueError, TypeError):
                return f"*Sección no válida: {seccion_str}*", "*No se pudo procesar la sección.*"
                
            concl = estado["trazas"].get(sec_id)
            if not concl:
                return f"No hay conclusiones para la sección {seccion_str}", ""
                
            conclusiones_texto = (
                f"**Tramo vial**: Sección {sec_id}\n"
                f"- **Condición Estructural (ICP)**: `{concl['condicion']}`\n"
                f"- **Nivel de Riesgo**: `{concl['riesgo']}`\n"
                f"- **Acción de Obra Recomendada**: `{concl['prioridad']}`"
            )
            
            return conclusiones_texto, concl["traza"]
            
        dropdown_sec.change(
            fn=mostrar_conclusiones_seccion,
            inputs=[dropdown_sec, estado_inspeccion],
            outputs=[out_concl, out_traza]
        )
        
        # Event 3: Re-evaluate expert system inferences dynamically (based on Rule Editor YAML)
        def ejecutar_reinferencia_workflow(seccion_str, estado):
            if not estado or "hechos" not in estado:
                raise gr.Error("Primero debe procesar un video vial en la pestaña 1.")
                
            if not seccion_str:
                raise gr.Error("Por favor, seleccione una sección válida en el menú desplegable.")
                
            try:
                sec_id = int(seccion_str)
            except (ValueError, TypeError):
                raise gr.Error(f"Sección no válida: {seccion_str}")
            
            # Filter base facts of the selected section
            hechos_filtrados = [
                h for h in estado["hechos"] 
                if h.nombre in ["falla_detectada", "seccion_analizada"] and h.obtener("seccion") == sec_id
            ]
            
            # Instantiate work memory and execute inference rules
            memoria = MemoriaTrabajo()
            for h in hechos_filtrados:
                memoria.agregar(h)
                
            traza = TrazaRazonamiento()
            procesador_global.motor.inferir(memoria, traza)
            
            # Extract resulting updated facts
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
                
            # Compile new explanation trace
            traza_md = traza.formatear_markdown(seccion_id=sec_id)
            
            conclusiones_texto = (
                f"⚠️ **INFERENCIA ACTUALIZADA (Reglas Modificadas):**\n"
                f"**Tramo vial**: Sección {sec_id}\n"
                f"- **Condición Estructural (ICP)**: `{cond_via}`\n"
                f"- **Nivel de Riesgo**: `{riesgo}`\n"
                f"- **Acción de Obra Recomendada**: `{prio_obra}`"
            )
            
            # Update trace cache in session state
            estado["trazas"][sec_id] = {
                "condicion": cond_via,
                "prioridad": prio_obra,
                "riesgo": riesgo,
                "traza": traza_md
            }
            
            # Recompile results table summary
            resumen_secciones = []
            for s_id, concl in estado["trazas"].items():
                num_f = len([h for h in hechos_filtrados if h.nombre == "falla_detectada"])
                num_b = len([h for h in hechos_filtrados if h.nombre == "falla_detectada" and h.obtener("tipo_falla") == "D40"])
                resumen_secciones.append({
                    "Sección": s_id,
                    "Total Fallas": num_f,
                    "Baches": num_b,
                    "Condición (ICP)": concl["condicion"],
                    "Prioridad Obra": concl["prioridad"],
                    "Nivel Riesgo": concl["riesgo"]
                })
            df_resumen = pd.DataFrame(resumen_secciones)
            estado["tabla_resumen"] = df_resumen
            
            return conclusiones_texto, traza_md, df_resumen
            
        btn_reinferir.click(
            fn=ejecutar_reinferencia_workflow,
            inputs=[dropdown_sec, estado_inspeccion],
            outputs=[out_concl, out_traza, tabla_metricas]
        )
        
    return demo

if __name__ == "__main__":
    app = build_app()
    # Permit local network connections for UNEXPO mechatronics classroom demonstrations
    app.launch(
        share=False,
        server_name="0.0.0.0",
        server_port=7860,
        theme=obtener_tema_gradio(),
        css=CSS_UNEXPO,
        max_file_size="500mb"
    )
