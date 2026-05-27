# -*- coding: utf-8 -*-
"""
Módulo de Interfaz de Usuario — Pavimentados UNEXPO.
Expone las funciones de construcción de pestañas de la aplicación Gradio y
el tema visual de la universidad.
"""

from .tema import CSS_UNEXPO, obtener_tema_gradio
from .pestanas.pestana_analisis import crear_pestana_analisis
from .pestanas.pestana_experto import crear_pestana_experto
from .pestanas.pestana_resultados import crear_pestana_resultados
from .pestanas.pestana_educacion import crear_pestana_educacion

__all__ = [
    'CSS_UNEXPO',
    'obtener_tema_gradio',
    'crear_pestana_analisis',
    'crear_pestana_experto',
    'crear_pestana_resultados',
    'crear_pestana_educacion'
]
