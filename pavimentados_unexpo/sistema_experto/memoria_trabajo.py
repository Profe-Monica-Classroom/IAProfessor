# -*- coding: utf-8 -*-
"""
Memoria de Trabajo del Sistema Experto UNEXPO.
Este módulo define la estructura de los Hechos (datos en memoria) y la
Memoria de Trabajo encargada de almacenar y buscar hechos durante la inferencia.
"""

class Hecho:
    """
    Representa un hecho o dato dentro de la Memoria de Trabajo del sistema experto.
    Cada hecho tiene un nombre categórico (ej: 'falla_detectada') y propiedades/atributos dinámicos.
    """
    def __init__(self, nombre: str, **propiedades):
        self.nombre = nombre
        self.propiedades = propiedades

    def obtener(self, clave: str, defecto=None):
        """Obtiene una propiedad del hecho."""
        return self.propiedades.get(clave, defecto)

    def __eq__(self, otro):
        if not isinstance(otro, Hecho):
            return False
        return self.nombre == otro.nombre and self.propiedades == otro.propiedades

    def __repr__(self):
        props_str = ", ".join(f"{k}={v}" for k, v in self.propiedades.items())
        return f"{self.nombre}({props_str})"


class MemoriaTrabajo:
    """
    Colección de hechos activos y conclusiones deducidas en un momento dado
    durante la ejecución del motor de inferencia.
    """
    def __init__(self):
        self.hechos = []

    def agregar(self, hecho: Hecho) -> bool:
        """
        Agrega un hecho a la memoria de trabajo.
        Retorna True si el hecho es nuevo y fue agregado, False si ya existía.
        """
        if hecho not in self.hechos:
            self.hechos.append(hecho)
            return True
        return False

    def obtener_por_nombre(self, nombre: str) -> list[Hecho]:
        """Retorna todos los hechos que coincidan con un nombre específico."""
        return [h for h in self.hechos if h.nombre == nombre]

    def existe(self, nombre: str, **condiciones) -> bool:
        """
        Verifica si existe un hecho con un nombre y condiciones específicas en sus propiedades.
        Ejemplo: memoria.existe('severidad', id_falla='F001', nivel='ALTA')
        """
        for hecho in self.obtener_por_nombre(nombre):
            cumple = True
            for k, v in condiciones.items():
                if hecho.obtener(k) != v:
                    cumple = False
                    break
            if cumple:
                return True
        return False

    def vaciar(self):
        """Limpia la memoria de trabajo."""
        self.hechos.clear()

    def __repr__(self):
        if not self.hechos:
            return "Memoria de Trabajo vacía."
        return "\n".join(f"- {hecho}" for hecho in self.hechos)
