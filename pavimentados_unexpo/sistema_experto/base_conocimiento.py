# -*- coding: utf-8 -*-
"""
Base de Conocimiento del Sistema Experto UNEXPO.
Este módulo define la clase Regla y los mecanismos para cargar reglas de
producción desde archivos YAML, evaluando sus condiciones sobre la Memoria de Trabajo.
"""

import os
import yaml
from .memoria_trabajo import Hecho, MemoriaTrabajo

def evaluar_operador(valor_hecho, operador: str, valor_esperado) -> bool:
    """Evalúa una comparación simple entre el valor de un hecho y un valor esperado."""
    if valor_hecho is None:
        return False
        
    try:
        if operador == "==":
            return valor_hecho == valor_esperado
        elif operador == "!=":
            return valor_hecho != valor_esperado
        elif operador == ">":
            return float(valor_hecho) > float(valor_esperado)
        elif operador == "<":
            return float(valor_hecho) < float(valor_esperado)
        elif operador == ">=":
            return float(valor_hecho) >= float(valor_esperado)
        elif operador == "<=":
            return float(valor_hecho) <= float(valor_esperado)
        elif operador == "in":
            if isinstance(valor_esperado, list):
                return valor_hecho in valor_esperado
            return str(valor_hecho) in str(valor_esperado)
        elif operador == "not in":
            if isinstance(valor_esperado, list):
                return valor_hecho not in valor_esperado
            return str(valor_hecho) not in str(valor_esperado)
    except (ValueError, TypeError):
        return False
    return False


class Regla:
    """
    Representa una regla de producción (SI-ENTONCES) en el sistema experto.
    """
    def __init__(self, id_regla: str, nombre: str, categoria: str, 
                 condiciones: list, accion: dict, explicacion: str, 
                 hecho_principal: str = None, referencia: str = ""):
        self.id = id_regla
        self.nombre = nombre
        self.categoria = categoria
        self.condiciones = condiciones
        self.accion = accion
        self.explicacion = explicacion
        self.hecho_principal = hecho_principal
        self.referencia = referencia

    def evaluar(self, memoria: MemoriaTrabajo) -> list[dict]:
        """
        Evalúa las condiciones de la regla sobre la memoria de trabajo.
        Retorna una lista de diccionarios de activaciones (bindings). Cada activación
        contiene las variables del hecho que satisfizo las condiciones.
        """
        activaciones = []
        
        if self.hecho_principal:
            # La regla se aplica a cada hecho del tipo 'hecho_principal'
            hechos_candidatos = memoria.obtener_por_nombre(self.hecho_principal)
            for hecho in hechos_candidatos:
                contexto = hecho.propiedades.copy()
                contexto['id_hecho_principal'] = id(hecho)
                
                cumple_todas = True
                for cond in self.condiciones:
                    if 'campo' in cond:
                        campo = cond['campo']
                        op = cond['operador']
                        val_esp = cond['valor']
                        val_hecho = hecho.obtener(campo)
                        
                        if not evaluar_operador(val_hecho, op, val_esp):
                            cumple_todas = False
                            break
                            
                    elif 'hecho_existe' in cond:
                        nombre_hecho_buscado = cond['hecho_existe']
                        conds_buscadas = cond.get('condiciones', {})
                        
                        # Reemplazar variables contextuales de la forma {variable}
                        conds_filtradas = {}
                        for k, v in conds_buscadas.items():
                            if isinstance(v, str) and v.startswith('{') and v.endswith('}'):
                                var_name = v[1:-1]
                                conds_filtradas[k] = contexto.get(var_name)
                            else:
                                conds_filtradas[k] = v
                                
                        if not memoria.existe(nombre_hecho_buscado, **conds_filtradas):
                            cumple_todas = False
                            break
                
                if cumple_todas:
                    activaciones.append(contexto)
        else:
            # Regla de evaluación global
            cumple_todas = True
            contexto = {}
            for cond in self.condiciones:
                if 'hecho_existe' in cond:
                    nombre_hecho_buscado = cond['hecho_existe']
                    conds_buscadas = cond.get('condiciones', {})
                    if not memoria.existe(nombre_hecho_buscado, **conds_buscadas):
                        cumple_todas = False
                        break
            if cumple_todas:
                activaciones.append(contexto)
                
        return activaciones

    def ejecutar_accion(self, contexto: dict) -> Hecho:
        """
        Genera un nuevo Hecho ejecutando la acción de la regla usando el contexto de activación.
        Reemplaza marcadores de posición tipo {variable} en las propiedades de la acción.
        """
        nombre_hecho = self.accion['hecho']
        props_accion = self.accion.get('propiedades', {})
        
        nuevas_props = {}
        for k, v in props_accion.items():
            if isinstance(v, str) and v.startswith('{') and v.endswith('}'):
                var_name = v[1:-1]
                nuevas_props[k] = contexto.get(var_name)
            else:
                nuevas_props[k] = v
                
        return Hecho(nombre_hecho, **nuevas_props)

    def __repr__(self):
        return f"Regla({self.id}: {self.nombre})"


def cargar_reglas_desde_yaml(ruta_archivo: str) -> list[Regla]:
    """Carga una lista de objetos Regla desde un archivo YAML."""
    if not os.path.exists(ruta_archivo):
        return []
        
    with open(ruta_archivo, 'r', encoding='utf-8') as f:
        datos = yaml.safe_load(f)
        
    if not datos or 'reglas' not in datos:
        return []
        
    reglas = []
    for r in datos['reglas']:
        reglas.append(Regla(
            id_regla=r['id'],
            nombre=r['nombre'],
            categoria=r['categoria'],
            condiciones=r['condiciones'],
            accion=r['accion'],
            explicacion=r['explicacion'],
            hecho_principal=r.get('hecho_principal'),
            referencia=r.get('referencia', "")
        ))
    return reglas
