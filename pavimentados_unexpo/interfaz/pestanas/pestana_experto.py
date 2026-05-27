# -*- coding: utf-8 -*-
"""
Pestaña del Sistema Experto — Pavimentados UNEXPO.
Implementa el panel interactivo del Sistema Experto, mostrando las trazas de
razonamiento secuenciales por sección y el Editor de Reglas YAML educativo.
"""

import os
import sys
import yaml
import gradio as gr
from pathlib import Path

# Agregar la raíz del paquete al sys.path para permitir importaciones absolutas
DIRECTORIO_PAQUETE = Path(__file__).resolve().parent.parent.parent
if str(DIRECTORIO_PAQUETE) not in sys.path:
    sys.path.insert(0, str(DIRECTORIO_PAQUETE))

from sistema_experto.base_conocimiento import cargar_reglas_desde_yaml

RUTA_REGLAS = DIRECTORIO_PAQUETE / "sistema_experto" / "reglas"


def crear_pestana_experto(procesador):
    """
    Construye la Pestaña 2: Sistema Experto de la app Gradio.
    Retorna componentes clave para enlazar eventos.
    """
    with gr.Row():
        # COLUMNA IZQUIERDA: Traza de Razonamiento
        with gr.Column(scale=6, elem_classes="glass-card"):
            gr.Markdown("### 🧠 Auditoría y Traza de Razonamiento")
            gr.Markdown("Explora el proceso deductivo paso a paso (Explicabilidad) aplicado en cada sección de la calzada.")
            
            # Selector de tramo analizado
            dropdown_seccion = gr.Dropdown(
                choices=["1"], 
                value="1", 
                label="Seleccionar Sección del Video", 
                interactive=True,
                info="Elije un tramo para auditar su cadena de inferencias."
            )
            
            btn_recargar_inferencia = gr.Button("🔄 Re-calcular Inferencia con Reglas Actuales", elem_classes="btn-secondary")
            
            gr.Markdown("**📋 Conclusiones en este Tramo Vial:**")
            output_conclusiones = gr.Markdown("*Suba y analice un video primero.*")
            
            gr.Markdown("**🧠 Registro Explicativo de Inferencia:**")
            output_traza = gr.Markdown(
                "*La traza de razonamiento aparecerá aquí en formato legible para auditoría de mecatrónica.*",
                elem_classes="monospaced-trace"
            )
            
        # COLUMNA DERECHA: Editor de Reglas Educativo
        with gr.Column(scale=5, elem_classes="glass-card"):
            gr.Markdown("### 🛠️ Editor de Reglas YAML (Base de Conocimiento)")
            gr.Markdown("¡Práctica en clase! Modifica las condiciones, prioridades o umbrales de las reglas y observa cómo cambia el razonamiento al instante.")
            
            # Selector de archivo de reglas
            selector_archivo_reglas = gr.Dropdown(
                choices=[
                    "reglas_severidad.yaml", 
                    "reglas_condicion.yaml", 
                    "reglas_mantenimiento.yaml", 
                    "reglas_seguridad.yaml"
                ],
                value="reglas_severidad.yaml",
                label="Seleccionar Archivo de Reglas a Editar",
                interactive=True
            )
            
            # Editor de Código
            codigo_reglas = gr.Code(
                label="Editor YAML de Reglas",
                language="yaml",
                interactive=True,
                lines=18
            )
            
            # Botones del editor
            with gr.Row():
                btn_guardar_reglas = gr.Button("💾 Guardar y Recargar Reglas", elem_classes="btn-primary")
                btn_restaurar_defecto = gr.Button("↩️ Restaurar Original", elem_classes="btn-secondary")
                
            output_status_reglas = gr.Markdown("*Cargado correctamente.*")
            
    # Funciones de utilidad interna del editor
    def leer_archivo_reglas(archivo_nombre):
        ruta_completa = RUTA_REGLAS / archivo_nombre
        try:
            with open(ruta_completa, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"# Error al cargar archivo: {e}"
            
    def guardar_archivo_reglas(archivo_nombre, nuevo_contenido):
        # Intentar parsear como YAML válido antes de guardar para evitar crasheos viales
        try:
            yaml.safe_load(nuevo_contenido)
        except Exception as e:
            return f"❌ **Error de Sintaxis YAML:** {e}. No se guardaron los cambios."
            
        ruta_completa = RUTA_REGLAS / archivo_nombre
        try:
            with open(ruta_completa, "w", encoding="utf-8") as f:
                f.write(nuevo_contenido)
            # Recargar reglas en el procesador principal
            procesador.reglas.clear()
            for r_name in ["reglas_severidad.yaml", "reglas_condicion.yaml", "reglas_mantenimiento.yaml", "reglas_seguridad.yaml"]:
                procesador.reglas.extend(cargar_reglas_desde_yaml(str(RUTA_REGLAS / r_name)))
            # Recargar motor
            procesador.motor.reglas = procesador.reglas
            procesador.motor.reglas.sort(key=lambda r: r.id)
            return "✅ **Reglas guardadas y cargadas en el Motor de Inferencia.**"
        except Exception as e:
            return f"❌ **Error al escribir en disco:** {e}"
            
    # Enlazar la carga inicial y cambio de archivo
    selector_archivo_reglas.change(
        fn=leer_archivo_reglas,
        inputs=[selector_archivo_reglas],
        outputs=[codigo_reglas]
    )
    
    # Enlazar el guardado
    btn_guardar_reglas.click(
        fn=guardar_archivo_reglas,
        inputs=[selector_archivo_reglas, codigo_reglas],
        outputs=[output_status_reglas]
    )
    
    return dropdown_seccion, output_conclusiones, output_traza, btn_recargar_inferencia, selector_archivo_reglas, codigo_reglas, btn_guardar_reglas
