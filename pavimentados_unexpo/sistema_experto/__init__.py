# -*- coding: utf-8 -*-
"""
Módulo del Sistema Experto Pavimentados UNEXPO.
Expone las clases principales para la base de conocimientos, memoria de trabajo,
traza de razonamiento y el motor de inferencia.
"""

from .memoria_trabajo import Hecho, MemoriaTrabajo
from .base_conocimiento import Regla, cargar_reglas_desde_yaml
from .traza_razonamiento import TrazaRazonamiento
from .motor import MotorInferencia

__all__ = [
    'Hecho',
    'MemoriaTrabajo',
    'Regla',
    'cargar_reglas_desde_yaml',
    'TrazaRazonamiento',
    'MotorInferencia'
]
