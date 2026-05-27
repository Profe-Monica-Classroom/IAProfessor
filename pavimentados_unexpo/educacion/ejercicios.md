# 📝 Guía de Prácticas y Ejercicios — Pavimentados UNEXPO

Esta guía de laboratorio contiene las actividades prácticas obligatorias para los estudiantes de la unidad curricular de Sistemas Expertos y Control Mecatrónico.

---

## 🎯 Práctica de Laboratorio 1: Formalización de Conocimiento e Inferencia en Calzada

### **Objetivos**:
1. Entender la diferencia funcional entre percepción conexionista y razonamiento simbólico.
2. Aprender a modificar una Base de Conocimientos viva codificada en YAML.
3. Evaluar el impacto de la modificación de reglas sobre el dictamen final de mantenimiento de vías.

---

## 🔧 Actividad 1: Auditoría de la Traza de Razonamiento

1. Abre la aplicación **Pavimentados UNEXPO**.
2. Sube el video de prueba vial en la pestaña **📹 Análisis de Video**.
3. Selecciona una Tasa de Muestreo de `2 FPS` y una Duración de Sección de `10 segundos`.
4. Haz clic en **▶️ Iniciar Análisis Vial** y espera a que la IA y el motor concluyan.
5. Ve a la pestaña **🧠 Sistema Experto** y selecciona la **Sección 1**.
6. **Responde en tu cuaderno de laboratorio**:
   - ¿Qué hechos iniciales fueron cargados en la Memoria de Trabajo para esta sección?
   - ¿Qué regla se disparó primero? Escribe su ID y explica por qué se cumplió su condición.
   - ¿Cuál fue la condición (ICP) final dictaminada para este tramo y qué acción de mantenimiento prescribió el sistema?

---

## 🛠️ Actividad 2: Reprogramación en Caliente del Cerebro Simbólico

Los ingenieros de la alcaldía local sugieren que, debido al incremento de lluvias en la región, la condición de vía `MALO` en pavimentos representa un riesgo inmediato para vehículos pequeños. Por lo tanto, exigen cambiar la prioridad técnica del mantenimiento correctivo de **ALTA** a **URGENTE**.

1. Ve a la pestaña **🧠 Sistema Experto**, sección derecha: **Editor de Reglas YAML**.
2. Selecciona el archivo `reglas_mantenimiento.yaml`.
3. Localiza la regla `R032` (Mantenimiento Correctivo con Parcheo Profundo).
4. **Modifica el código YAML**:
   - Cambia `prioridad: "ALTA"` por `prioridad: "URGENTE"`.
5. Haz clic en **💾 Guardar y Recargar Reglas**. Asegúrate de ver el mensaje de confirmación verde en la pantalla.
6. En la sección izquierda del panel, haz clic en **🔄 Re-calcular Inferencia con Reglas Actuales**.
7. **Audita el cambio**:
   - Examina el panel de **Conclusiones en este Tramo Vial**. ¿Cuál es la nueva prioridad recomendada para el tramo?
   - Revisa la **Traza de Razonamiento**. ¿Qué regla se disparó y qué hecho final se registró en la memoria de trabajo?

---

## 📝 Preguntas de Discusión y Control

1. **¿Qué sucede si subimos un video donde no se detecta absolutamente ningún daño?**
   - Sigue la cadena lógica del motor. ¿Qué regla de la base de conocimientos se activaría? ¿Cuál sería el ICP y la prioridad?
2. **Ventaja del desacoplamiento de la base de conocimiento**:
   - Explica por qué pudimos cambiar el comportamiento del sistema de prioridad ALTA a URGENTE en menos de 50 milisegundos sin necesidad de volver a entrenar la red neuronal YOLOv8 (lo cual tomaría horas o días de cómputo GPU).
3. **Formalización de Reglas**:
   - Diseña en pseudocódigo o YAML una regla nueva (`R046`) que evalúe si el desgaste de las marcas viales (D43/D44) es superior a 2 detecciones y dictamine una recomendación de demarcación horizontal prioritaria.
