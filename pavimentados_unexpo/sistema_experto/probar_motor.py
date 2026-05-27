# -*- coding: utf-8 -*-
"""
Script de prueba para el Sistema Experto Pavimentados UNEXPO.
Permite ejecutar el motor de inferencia en frío con datos simulados (mockups)
para verificar que las reglas funcionen correctamente y auditar la traza.
"""

import os
from .memoria_trabajo import Hecho, MemoriaTrabajo
from .base_conocimiento import cargar_reglas_desde_yaml
from .motor import MotorInferencia
from .traza_razonamiento import TrazaRazonamiento



def probar():
    print("🚀 Iniciando prueba del Sistema Experto Pavimentados UNEXPO...")
    
    # 1. Definir rutas a los archivos de reglas
    carpeta_reglas = os.path.join(os.path.dirname(__file__), "reglas")
    ruta_severidad = os.path.join(carpeta_reglas, "reglas_severidad.yaml")
    ruta_condicion = os.path.join(carpeta_reglas, "reglas_condicion.yaml")
    ruta_mantenimiento = os.path.join(carpeta_reglas, "reglas_mantenimiento.yaml")
    ruta_seguridad = os.path.join(carpeta_reglas, "reglas_seguridad.yaml")
    
    # 2. Cargar todas las reglas
    print("\n📚 Cargando base de conocimiento...")
    reglas = []
    reglas.extend(cargar_reglas_desde_yaml(ruta_severidad))
    reglas.extend(cargar_reglas_desde_yaml(ruta_condicion))
    reglas.extend(cargar_reglas_desde_yaml(ruta_mantenimiento))
    reglas.extend(cargar_reglas_desde_yaml(ruta_seguridad))
    
    print(f"   Cargadas {len(reglas)} reglas de producción en total.")
    
    # 3. Crear memoria de trabajo e inyectar hechos iniciales simulados
    print("\n📋 Población de la Memoria de Trabajo (Detecciones Simuladas de la Sección 5)...")
    memoria = MemoriaTrabajo()
    
    # Falla 1: Un bache profundo (D40) en la sección 5
    memoria.agregar(Hecho("falla_detectada", id_falla="F001", seccion=5, tipo_falla="D40", area_deteccion=6200, confianza=0.89))
    
    # Falla 2: Grieta en piel de cocodrilo moderada (D10) en la sección 5
    memoria.agregar(Hecho("falla_detectada", id_falla="F002", seccion=5, tipo_falla="D10", area_deteccion=4500, confianza=0.82))
    
    # Falla 3: Grieta longitudinal menor (D00) en la sección 5
    memoria.agregar(Hecho("falla_detectada", id_falla="F003", seccion=5, tipo_falla="D00", area_deteccion=1200, confianza=0.76))
    
    # Falla 4: Desgaste de marcas viales (D43) en la sección 5
    memoria.agregar(Hecho("falla_detectada", id_falla="F004", seccion=5, tipo_falla="D43", area_deteccion=2300, confianza=0.45))
    
    # Datos globales de la sección 5 agregados al finalizar el conteo por el procesador
    memoria.agregar(Hecho("seccion_analizada", seccion=5, num_fallas=4, num_baches=1, num_piel_cocodrilo=1, num_marcas_desgastadas=1))
    
    print("   Hechos cargados:")
    for h in memoria.hechos:
        print(f"    - {h}")
        
    # 4. Inicializar motor e inferir con traza de razonamiento
    print("\n🧠 Ejecutando el Motor de Inferencia (Encadenamiento Hacia Adelante)...")
    traza = TrazaRazonamiento()
    motor = MotorInferencia(reglas)
    
    num_disparos = motor.inferir(memoria, traza)
    print(f"   Inferencia completada. ¡Se dispararon {num_disparos} reglas!")
    
    # 5. Imprimir la traza de razonamiento educativo
    print("\n" + "=" * 60)
    print(traza.formatear_texto_plano(seccion_id=5))
    print("=" * 60)
    
    # 6. Imprimir conclusiones específicas
    print("\n💡 Recomendaciones Finales Extraídas para la Sección 5:")
    condiciones = memoria.obtener_por_nombre("condicion_via")
    mantenimientos = memoria.obtener_por_nombre("mantenimiento")
    riesgos = memoria.obtener_por_nombre("riesgo_seguridad")
    
    if condiciones:
        print(f"   - Condición del Tramo: {condiciones[0].obtener('indice')}")
    if riesgos:
        print(f"   - Nivel de Riesgo de Seguridad: {riesgos[0].obtener('nivel')} - {riesgos[0].obtener('descripcion')}")
    if mantenimientos:
        print(f"   - Acción de Mantenimiento Recomendada: {mantenimientos[0].obtener('accion_recomendada')}")
        print(f"   - Prioridad de Ejecución: {mantenimientos[0].obtener('prioridad')}")

if __name__ == "__main__":
    probar()
