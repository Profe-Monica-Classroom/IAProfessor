# -*- coding: utf-8 -*-
"""
Motor de Inferencia del Sistema Experto UNEXPO.
Implementa un motor de encadenamiento hacia adelante (forward chaining) con
resolución de conflictos y prevención de ciclos infinitos.
"""

from .memoria_trabajo import Hecho, MemoriaTrabajo
from .base_conocimiento import Regla
from .traza_razonamiento import TrazaRazonamiento

class MotorInferencia:
    """
    Motor de Inferencia de producción por encadenamiento hacia adelante.
    Aplica las reglas disponibles a la memoria de trabajo hasta alcanzar un punto fijo
    (donde no se puedan derivar más hechos).
    """
    def __init__(self, reglas: list[Regla]):
        self.reglas = reglas
        # Ordenamos las reglas por ID para garantizar consistencia y orden educativo
        self.reglas.sort(key=lambda r: r.id)

    def inferir(self, memoria: MemoriaTrabajo, traza: TrazaRazonamiento = None) -> int:
        """
        Ejecuta el ciclo de inferencia.
        Retorna la cantidad de reglas que se dispararon.
        """
        if traza:
            traza.registrar_hechos_iniciales(memoria.hechos)
            
        disparos_realizados = set()  # Para evitar disparar la misma regla sobre el mismo hecho repetidamente
        reglas_disparadas_total = 0
        hubo_cambio = True

        while hubo_cambio:
            hubo_cambio = False
            
            # En cada iteración buscamos reglas aplicables
            for regla in self.reglas:
                # Evaluamos la regla sobre la memoria de trabajo actual
                activaciones = regla.evaluar(memoria)
                
                for contexto in activaciones:
                    # Creamos una clave única para esta activación y regla
                    # Si la regla está asociada a un hecho principal, usamos su id en memoria
                    if 'id_hecho_principal' in contexto:
                        clave_disparo = (regla.id, contexto['id_hecho_principal'])
                    else:
                        # Si es global, usamos una clave basada en los valores del contexto
                        items_ordenados = tuple(sorted((k, str(v)) for k, v in contexto.items() if k != 'id_hecho_principal'))
                        clave_disparo = (regla.id, items_ordenados)
                        
                    if clave_disparo in disparos_realizados:
                        continue  # Ya disparamos esta regla para este contexto específico
                        
                    # Ejecutamos la acción de la regla
                    nuevo_hecho = regla.ejecutar_accion(contexto)
                    
                    # Intentamos agregarlo a la memoria de trabajo
                    fue_agregado = memoria.agregar(nuevo_hecho)
                    
                    # Registramos el disparo
                    disparos_realizados.add(clave_disparo)
                    
                    if fue_agregado:
                        reglas_disparadas_total += 1
                        hubo_cambio = True
                        
                        if traza:
                            # Formateamos una lista de condiciones legibles para la traza
                            conds_legibles = []
                            for cond in regla.condiciones:
                                if 'campo' in cond:
                                    val_real = contexto.get(cond['campo'])
                                    conds_legibles.append(f"{cond['campo']}({val_real}) {cond['operador']} {cond['valor']}")
                                elif 'hecho_existe' in cond:
                                    # Formatear condiciones buscadas de forma legible
                                    conds_buscadas = cond.get('condiciones', {})
                                    conds_buscadas_legibles = {k: (contexto.get(v[1:-1]) if isinstance(v, str) and v.startswith('{') and v.endswith('}') else v) for k, v in conds_buscadas.items()}
                                    conds_legibles.append(f"Existe Hecho({cond['hecho_existe']} con {conds_buscadas_legibles})")
                            
                            traza.registrar_paso(
                                regla_id=regla.id,
                                regla_nombre=regla.nombre,
                                condiciones=conds_legibles,
                                resultado=nuevo_hecho
                            )
                            
                        # Si cambiamos la memoria, volvemos a evaluar desde la regla con mayor prioridad (R001...)
                        # Esto implementa la estrategia de resolución de conflictos de "prioridad estructural"
                        break
                
                if hubo_cambio:
                    break  # Reinicia el ciclo for de reglas con la memoria de trabajo actualizada
            
            # Salvaguarda educativa: evitar ciclos infinitos si el contador supera un límite razonable
            if reglas_disparadas_total > 500:
                print("⚠️ ADVERTENCIA: Se superó el límite de disparos (posible bucle infinito en reglas).")
                break
                
        if traza:
            traza.registrar_hechos_finales(memoria.hechos)
            
        return reglas_disparadas_total
