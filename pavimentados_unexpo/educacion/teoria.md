# 📚 Sistemas Basados en Conocimiento y IA Híbrida — UNEXPO

Este documento contiene el marco teórico del caso de estudio **Pavimentados UNEXPO**, diseñado para la unidad curricular de Sistemas Expertos y Control Mecatrónico.

---

## 1. ¿Qué es un Sistema Experto?

Un **Sistema Experto** (SE) es una rama de la Inteligencia Artificial Simbólica diseñada para resolver problemas en un dominio muy específico, imitando el razonamiento lógico de un experto humano en la materia.

A diferencia del Aprendizaje Automático (Machine Learning), que aprende de forma inductiva extrayendo patrones estadísticos desde millones de datos numéricos (caja negra), los Sistemas Expertos operan de forma **deductiva**. Utilizan conocimiento formalizado explícitamente por ingenieros de conocimiento y expertos del dominio en forma de **Reglas de Producción**.

---

## 2. Componentes Fundamentales de la Arquitectura

La arquitectura clásica de un Sistema Basado en Reglas consta de tres elementos esenciales:

### A. La Base de Conocimiento (Knowledge Base)
Es el repositorio donde se almacena el saber de la especialidad. En nuestro sistema, este saber está codificado en archivos legibles con formato **YAML** utilizando reglas del tipo `SI <condiciones> ENTONCES <acción>`.

*Ejemplo:*
```yaml
SI:
  tipo_falla == "D40" (Bache Abierto)
  area_deteccion > 5000 pixeles
ENTONCES:
  severidad = "CRITICA"
```

### B. La Memoria de Trabajo (Working Memory)
Es el espacio de almacenamiento temporal y dinámico que guarda los hechos observados en el entorno (como las detecciones obtenidas por visión por computadora) y todas las nuevas conclusiones parciales deducidas en tiempo real.

*Hecho Inicial:* `falla_detectada(tipo=D40, area=6200)`
*Hecho Deducido:* `severidad(id=F001, nivel=CRITICA)`

### C. El Motor de Inferencia (Inference Engine)
Es el cerebro del sistema. Ejecuta la lógica deductiva aplicando las reglas sobre la memoria de trabajo. El motor de Pavimentados UNEXPO opera bajo la estrategia de **Encadenamiento Hacia Adelante (Forward Chaining)**:
1. Compara las condiciones de todas las reglas contra los hechos de la memoria de trabajo.
2. Si las condiciones se cumplen, activa la regla (la añade a la agenda).
3. Resuelve conflictos de disparos (ejecutando primero las reglas de mayor prioridad estructural).
4. Dispara la regla, agregando su conclusión como un nuevo hecho en la Memoria de Trabajo.
5. Repite recursivamente hasta alcanzar un **punto fijo** (donde no es posible deducir nada nuevo).

---

## 3. Explicabilidad y Traza de Razonamiento

Una ventaja crucial de los Sistemas Expertos sobre el Deep Learning es la **transparencia y explicabilidad**. Puesto que cada paso lógico se ejecuta mediante una regla explícita, el sistema puede generar una **Traza de Razonamiento** secuencial. Esto permite auditar y certificar cada dictamen ante ingenieros civiles viales, indicando exactamente qué regla se activó, qué condición se cumplió y qué conclusión se dedujo.

---

## 4. IA Híbrida: Conexiones y Símbolos

El sistema **Pavimentados UNEXPO** es un modelo de **IA Híbrida** (Neuro-Simbólica):

1. **Capa Conexionista (Deep Learning - YOLOv8)**: Se encarga de la **percepción**. Recibe los pixeles crudos del video vial y reconoce dónde están las grietas y baches, localizando sus coordenadas. Esto simula el aparato visual.
2. **Capa Simbólica (Sistema Experto - Reglas de Producción)**: Se encarga del **razonamiento cognitivo**. Recibe los datos estructurados de la capa visual y aplica las normas técnicas para catalogar el estado del pavimento y prescribir las obras públicas necesarias.
