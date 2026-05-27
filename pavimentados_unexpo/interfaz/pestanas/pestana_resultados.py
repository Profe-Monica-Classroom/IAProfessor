# -*- coding: utf-8 -*-
"""
Pestaña de Resultados y Métricas — Pavimentados UNEXPO.
Muestra el dashboard analítico con la tabla resumen de tramos, el gráfico de
distribución de fallas y genera reportes descargables en español.
"""

import os
import pandas as pd
import gradio as gr
from pathlib import Path

DIRECTORIO_RAIZ = Path(__file__).resolve().parent.parent.parent

def crear_pestana_resultados(procesador):
    """
    Construye la Pestaña 3: Resultados y Métricas de la app Gradio.
    Retorna componentes clave para enlazar eventos.
    """
    with gr.Row():
        with gr.Column(scale=6, elem_classes="glass-card"):
            gr.Markdown("### 📊 Dashboard de la Condición Vial por Tramos")
            gr.Markdown("Resumen unificado por secciones. Cada sección representa virtualmente 100 metros de vialidad analizada.")
            
            # Tabla resumen de datos viales
            tabla_resumen = gr.Dataframe(
                headers=["Sección", "Total Fallas", "Baches", "Condición (ICP)", "Prioridad Obra", "Nivel Riesgo"],
                datatype=["number", "number", "number", "str", "str", "str"],
                label="Tabla Resumen de Tramos Viales",
                interactive=False,
                elem_classes="dataframe-container"
            )
            
            # Botón para descargar el reporte de ingeniería
            btn_reporte = gr.Button("📝 Generar y Descargar Reporte Técnico", elem_classes="btn-primary")
            output_reporte_file = gr.File(label="Descargar Reporte (.md)")
            
        with gr.Column(scale=5, elem_classes="glass-card"):
            gr.Markdown("### 📈 Distribución Estadística de Daños")
            gr.Markdown("Gráfico analítico que ilustra las frecuencias relativas de cada clase de falla detectada.")
            
            # Gráfico de distribución de fallas
            imagen_grafico = gr.Image(
                label="Distribución de Daños en Calzada",
                show_label=True,
                interactive=False
            )
            
            gr.Markdown("### 📝 Resumen Ejecutivo")
            output_resumen_ejecutivo = gr.Markdown(
                "**Total Secciones Analizadas**: -\n"
                "**Estado Promedio del Pavimento**: -\n"
                "**Tramos Críticos / Urgentes**: -\n"
                "**Baches Abiertos Totales**: -"
            )
            
    # Función para generar un archivo con reporte en formato Markdown descargable
    def generar_reporte_tecnico(df_resumen):
        if df_resumen is None or len(df_resumen) == 0:
            return None
            
        ruta_reporte = DIRECTORIO_RAIZ / "pavimentados_unexpo" / "ejemplos" / "reporte_tecnico_vial.md"
        
        # Calcular algunas estadísticas
        total_secciones = len(df_resumen)
        baches_totales = int(df_resumen["Baches"].sum())
        total_fallas = int(df_resumen["Total Fallas"].sum())
        
        secciones_urgentes = len(df_resumen[df_resumen["Prioridad Obra"] == "URGENTE"])
        secciones_altas = len(df_resumen[df_resumen["Prioridad Obra"] == "ALTA"])
        
        conteo_icp = df_resumen["Condición (ICP)"].value_counts()
        icp_mas_comun = conteo_icp.index[0] if not conteo_icp.empty else "N/D"
        
        # Escribir reporte técnico en español
        try:
            with open(ruta_reporte, "w", encoding="utf-8") as f:
                f.write(f"# 🛠️ REPORTE TÉCNICO DE AUDITORÍA VIAL VIRTUAL — UNEXPO\n")
                f.write(f"**Fecha del Análisis**: May-2026\n")
                f.write(f"**Institución**: Universidad Nacional Experimental Politécnica (UNEXPO) — Mecatrónica\n")
                f.write(f"**Sistema**: Pavimentados UNEXPO (IA Conexionista YOLOv8 + IA Simbólica SE)\n")
                f.write(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n")
                
                f.write(f"## 1. RESUMEN EJECUTIVO\n")
                f.write(f"- **Distancia Total Evaluada**: {total_secciones * 100} metros viales ({total_secciones} secciones de 100m).\n")
                f.write(f"- **Total Fallas Estructurales Detectadas**: {total_fallas} fallas.\n")
                f.write(f"- **Total Baches Abiertos (Riesgo Crítico)**: {baches_totales} unidades.\n")
                f.write(f"- **Condición Vial Predominante (ICP)**: **{icp_mas_comun}**.\n")
                f.write(f"- **Tramos en Emergencia / Prioridad URGENTE**: {secciones_urgentes} tramo(s).\n")
                f.write(f"- **Tramos con Prioridad de Intervención ALTA**: {secciones_altas} tramo(s).\n\n")
                
                f.write(f"## 2. DETALLE ANALÍTICO DE INTERVENCIONES POR SECCIÓN\n")
                f.write(f"A continuación se detallan las métricas recolectadas por percepción profunda y las prescripciones dictaminadas por la base de conocimientos experta:\n\n")
                
                # Escribir tabla en markdown
                f.write(f"| Sección | Total Fallas | Baches | Condición (ICP) | Prioridad Obra | Nivel Riesgo |\n")
                f.write(f"|:---:|:---:|:---:|:---:|:---:|:---:|\n")
                for _, row in df_resumen.iterrows():
                    f.write(f"| Secc. {row['Sección']} | {row['Total Fallas']} | {row['Baches']} | {row['Condición (ICP)']} | **{row['Prioridad Obra']}** | {row['Nivel Riesgo']} |\n")
                
                f.write(f"\n\n## 3. RECOMENDACIONES DE INGENIERÍA DE MANTENIMIENTO\n")
                f.write(f"Basados en las reglas de la base de conocimientos y el Manual de Inspección INVIAS:\n\n")
                
                for _, row in df_resumen.iterrows():
                    sec_id = row['Sección']
                    icp = row['Condición (ICP)']
                    prio = row['Prioridad Obra']
                    
                    if prio in ["URGENTE", "ALTA"]:
                        f.write(f"### 📍 Sección {sec_id} — Prioridad: **{prio}**\n")
                        f.write(f"- **Condición de Pavimento**: {icp}\n")
                        
                        if icp == "MUY_MALO":
                            f.write(f"- **Acción Técnica**: Fresado integral de la carpeta de rodadura desgastada, compactación de base y colocación de una nueva mezcla asfáltica en caliente de 3 pulgadas.\n")
                        elif icp == "MALO":
                            f.write(f"- **Acción Técnica**: Bacheo profundo de baches abiertos, limpieza y soplado de grietas activas en piel de cocodrilo, y sellado con asfalto líquido elastomérico.\n")
                        else:
                            f.write(f"- **Acción Técnica**: Sellado puntual de grietas y bacheo superficial preventivo.\n")
                        f.write(f"\n")
                        
                f.write(f"\n---\n*Reporte generado por Pavimentados UNEXPO de forma automatizada.*")
                
            return str(ruta_reporte)
        except Exception as e:
            print(f"Error al escribir reporte descargable: {e}")
            return None
            
    btn_reporte.click(
        fn=generar_reporte_tecnico,
        inputs=[tabla_resumen],
        outputs=[output_reporte_file]
    )
    
    return tabla_resumen, imagen_grafico, output_resumen_ejecutivo, btn_reporte, output_reporte_file
