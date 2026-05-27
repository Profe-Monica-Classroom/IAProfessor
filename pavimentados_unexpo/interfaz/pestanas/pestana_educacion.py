# -*- coding: utf-8 -*-
"""
Pestaña de Educación y Teoría — Pavimentados UNEXPO.
Implementa el marco teórico del sistema experto, cuestionarios interactivos
para evaluar a los alumnos, y guías de prácticas de laboratorio en español.
"""

import os
import gradio as gr
from pathlib import Path

DIRECTORIO_RAIZ = Path(__file__).resolve().parent.parent.parent

def crear_pestana_educacion(procesador):
    """
    Construye la Pestaña 4: Educación y Teoría de la app Gradio.
    Retorna componentes de UI.
    """
    
    with gr.Row():
        # COLUMNA IZQUIERDA: Marco Teórico y Ejercicios
        with gr.Column(scale=6, elem_classes="glass-card"):
            gr.Markdown("### 📚 Unidad Académica: Sistemas Expertos e IA Híbrida")
            gr.Markdown("Este laboratorio interactivo demuestra la combinación de **IA Conexionista** (Deep Learning para percepción de imágenes) con la **IA Simbólica** (Sistemas basados en reglas de producción para razonar y decidir).")
            
            # Selector de lectura
            selector_tema = gr.Radio(
                choices=["1. ¿Qué es un Sistema Experto?", "2. Arquitectura de Pavimentados UNEXPO", "3. Guía de Práctica de Laboratorio"],
                value="1. ¿Qué es un Sistema Experto?",
                label="Selecciona la lectura de la guía de estudio:",
                interactive=True
            )
            
            # Contenedor del material teórico
            visor_teoria = gr.Markdown()
            
        # COLUMNA DERECHA: Cuestionario Interactivo para Alumnos
        with gr.Column(scale=5, elem_classes="glass-card"):
            gr.Markdown("### 📝 Cuestionario de Evaluación Vial (Quiz)")
            gr.Markdown("Responde las siguientes preguntas conceptuales y valida tu comprensión al instante.")
            
            # Pregunta 1
            p1 = gr.Radio(
                choices=[
                    "A) Aprender de millones de ejemplos para generalizar patrones estadísticos.",
                    "B) Representar conocimiento experto de forma explícita mediante reglas SI-ENTONCES.",
                    "C) Resolver integrales triples mediante algoritmos genéticos combinatorios."
                ],
                label="Pregunta 1: ¿Cuál es el objetivo principal de una Base de Conocimientos en un Sistema Experto?",
                interactive=True
            )
            
            # Pregunta 2
            p2 = gr.Radio(
                choices=[
                    "A) Encadenamiento hacia atrás (Backward Chaining) buscando causas.",
                    "B) Búsqueda en anchura no informada sobre grafos de decisión.",
                    "C) Encadenamiento hacia adelante (Forward Chaining) derivando conclusiones desde hechos iniciales."
                ],
                label="Pregunta 2: ¿Qué mecanismo usa el motor de inferencia de Pavimentados UNEXPO?",
                interactive=True
            )
            
            # Pregunta 3
            p3 = gr.Radio(
                choices=[
                    "A) La Memoria de Trabajo (facts store) inicial e intermedia.",
                    "B) La GPU Nvidia por acelerar el cómputo de matrices convolucionales.",
                    "C) La traza de razonamiento explicativa (Explicabilidad)."
                ],
                label="Pregunta 3: ¿Qué componente permite la transparencia y auditoría del sistema ante el usuario?",
                interactive=True
            )
            
            btn_evaluar = gr.Button("✔️ Verificar Respuestas", elem_classes="btn-primary")
            output_evaluacion = gr.Markdown()
            
    # Datos teóricos estáticos para evitar accesos lentos en disco
    TEORIA_1 = """
### 🧠 1. ¿Qué es un Sistema Experto?
Un **Sistema Experto** (SE) es un programa informático diseñado para simular el proceso de toma de decisiones y resolución de problemas de un experto humano en un dominio específico.

Pertenece a la **Inteligencia Artificial Simbólica** (Good Old-Fashioned AI - GOFAI). A diferencia de los modelos conexionistas (como las redes neuronales profundas), los sistemas expertos no aprenden de ejemplos, sino que son **alimentados explícitamente con el conocimiento recopilado** de expertos e ingenieros.

#### Componentes Fundamentales:
1. **Base de Conocimiento**: Contiene las leyes, directrices y verdades del dominio, usualmente representadas en forma de **Reglas de Producción** (`SI condiciones ENTONCES acción`).
2. **Memoria de Trabajo**: Almacena los hechos iniciales aportados y todas las conclusiones intermedias y finales deducidas durante el ciclo de razonamiento.
3. **Motor de Inferencia**: El núcleo lógico que aplica las reglas de la base de conocimientos sobre los hechos de la memoria de trabajo para derivar nuevo conocimiento.
4. **Módulo de Explicabilidad (Traza)**: El mecanismo que detalla y registra cada paso deductivo, respondiendo a la pregunta de *¿por qué el sistema tomó esta decisión?*.
"""

    TEORIA_2 = """
### 🏗️ 2. Arquitectura de Pavimentados UNEXPO
Este sistema es un ejemplo clásico y sumamente potente de un **Sistema de Inteligencia Artificial Híbrido**.

```
  [ Video Vial ]
        │
        ▼ (IA Conexionista - Aprendizaje Profundo)
┌──────────────────────────────────────────────┐
│  Percepción: YOLOv8 Object Detection Model   │  <- Detecta cajas crudas: D40, D10...
└──────────────────────────────────────────────┘
        │
        ▼ (Módulo de Integración y Traducción)
┌──────────────────────────────────────────────┐
│  Hechos Iniciales inyectados en Memoria      │  <- falla_detectada(tipo=D40, area=6200)
└──────────────────────────────────────────────┘
        │
        ▼ (IA Simbólica - Razonamiento Determinado)
┌──────────────────────────────────────────────┐
│  Motor de Inferencia (Forward Chaining)      │  <- Evalúa reglas YAML viales en orden
└──────────────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────────────┐
│  Prescripción: Conclusiones y Reporte Técnico│  <- Condición: MALO, Prioridad: ALTA
└──────────────────────────────────────────────┘
```

#### ¿Por qué usar un enfoque híbrido?
- **YOLOv8** es excelente para la **percepción** (ver dónde está la grieta, identificar patrones visuales complejos con pixeles), pero es una 'caja negra' que no puede justificar lógicamente por qué dictamina una obra civil.
- **El Sistema Experto** es sobresaliente para el **razonamiento lógico**, la justificación técnica, y la toma de decisiones basada en estándares legales e ingenieriles (INVIAS/ASTM), permitiendo auditar y editar las políticas directamente.
"""

    TEORIA_3 = """
### 🛠️ 3. Guía de Práctica de Laboratorio

#### **Objetivo**:
Aprender a formalizar conocimiento de ingeniería en reglas de producción y evaluar el impacto de la base de conocimientos en un sistema híbrido de inspección vial.

#### **Pasos recomendados para los estudiantes**:
1. **Paso 1**: Ve a la pestaña **📹 Análisis de Video** y procesa el video de demostración. Observa las detecciones visuales y el HUD en el video.
2. **Paso 2**: Entra en la pestaña **🧠 Sistema Experto**, selecciona una sección (ej. Sección 1) y audita con atención la **Traza de Razonamiento**. Entiende por qué se derivaron la severidad, condición y mantenimiento.
3. **Paso 3**: En el **Editor de Reglas (Base de Conocimiento)**, selecciona `reglas_mantenimiento.yaml`.
4. **Paso 4**: **Modifica una regla**: Edita la prioridad recomendada para la condición `MALO` en la regla `R032`. Cambia `prioridad: "ALTA"` por `prioridad: "CRITICA"`.
5. **Paso 5**: Haz clic en **💾 Guardar y Recargar Reglas**.
6. **Paso 6**: Haz clic en **🔄 Re-calcular Inferencia con Reglas Actuales**.
7. **Paso 7**: Comprueba que la prioridad en la sección correspondiente cambió instantáneamente de ALTA a CRÍTICA y observa el nuevo disparo en la traza. ¡Has reprogramado el cerebro simbólico del robot inspector en caliente!
"""

    def cambiar_lectura(seleccion):
        if "1." in seleccion:
            return TEORIA_1
        elif "2." in seleccion:
            return TEORIA_2
        else:
            return TEORIA_3
            
    # Enlazar selector de lectura
    selector_tema.change(
        fn=cambiar_lectura,
        inputs=[selector_tema],
        outputs=[visor_teoria]
    )
    
    # Carga inicial por defecto
    visor_teoria.value = TEORIA_1
    
    # Función para corregir y evaluar el quiz en español
    def corregir_quiz(res1, res2, res3):
        nota = 0
        feedback = []
        feedback.append("### 📝 REPORTE DE EVALUACIÓN DE SISTEMAS EXPERTOS\n")
        feedback.append("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
        
        # P1 Correcta: B
        if res1 and res1.startswith("B)"):
            nota += 1
            feedback.append("✅ **Pregunta 1: ¡Correcto!** La Base de Conocimientos tiene por objetivo almacenar el conocimiento explícito en reglas SI-ENTONCES.")
        else:
            feedback.append("❌ **Pregunta 1: Incorrecto.** Las redes neuronales aprenden de ejemplos (A). La base de conocimientos almacena lógica experta declarada en reglas (B).")
            
        # P2 Correcta: C
        if res2 and res2.startswith("C)"):
            nota += 1
            feedback.append("✅ **Pregunta 2: ¡Excelente!** Se inyectan las detecciones y se encadena hacia adelante hasta inferir prioridades viales.")
        else:
            feedback.append("❌ **Pregunta 2: Incorrecto.** El sistema experto inyecta hechos de la carretera y deduce conclusiones (encadenamiento hacia adelante, opción C).")
            
        # P3 Correcta: C
        if res3 and res3.startswith("C)"):
            nota += 1
            feedback.append("✅ **Pregunta 3: ¡Correcto!** La facilidad de explicación y la traza de razonamiento garantizan la transparencia del sistema.")
        else:
            feedback.append("❌ **Pregunta 3: Incorrecto.** La traza de razonamiento explicativa (C) es la que dota de explicabilidad e inteligibilidad al sistema experto.")
            
        feedback.append("\n" + "─" * 45)
        nota_sobre_20 = int((nota / 3) * 20)
        
        color_nota = "green" if nota_sobre_20 >= 14 else "red"
        feedback.append(f"### 🎯 CALIFICACIÓN FINAL: <span style='color:{color_nota}'>{nota_sobre_20} / 20 puntos</span>")
        
        if nota_sobre_20 == 20:
            feedback.append("🎉 ¡Felicitaciones! Has comprendido perfectamente la teoría de IA Híbrida y Sistemas Expertos. ¡Listo para la mecatrónica del futuro!")
        elif nota_sobre_20 >= 13:
            feedback.append("👍 ¡Buen esfuerzo! Repasa los conceptos errados y vuelve a intentarlo.")
        else:
            feedback.append("📚 Se recomienda volver a leer la sección '1. ¿Qué es un Sistema Experto?' para consolidar tus fundamentos.")
            
        return "\n".join(feedback)

    btn_evaluar.click(
        fn=corregir_quiz,
        inputs=[p1, p2, p3],
        outputs=[output_evaluacion]
    )

    return visor_teoria, p1, p2, p3, btn_evaluar, output_evaluacion
