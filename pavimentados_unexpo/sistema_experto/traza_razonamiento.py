# -*- coding: utf-8 -*-
"""
Traza de Razonamiento del Sistema Experto UNEXPO.
Registra paso a paso el proceso de inferencia para que los estudiantes
puedan auditar y aprender cómo se alcanzan las conclusiones (Explicabilidad).
"""

from datetime import datetime

class PasoInferencia:
    """Representa un único paso o disparo de regla durante el razonamiento."""
    def __init__(self, numero: int, regla_id: str, regla_nombre: str, 
                 condiciones_cumplidas: list, hecho_resultado: str):
        self.numero = numero
        self.regla_id = regla_id
        self.regla_nombre = regla_nombre
        self.condiciones_cumplidas = condiciones_cumplidas  # Lista de representaciones legibles de las condiciones
        self.hecho_resultado = hecho_resultado
        self.timestamp = datetime.now()


class TrazaRazonamiento:
    """
    Registra y formatea toda la cadena de razonamiento y disparos de reglas.
    """
    def __init__(self):
        self.hechos_iniciales = []
        self.pasos = []
        self.hechos_finales = []

    def registrar_hechos_iniciales(self, hechos: list):
        """Registra los hechos de partida cargados desde el subsistema de detección ML."""
        self.hechos_iniciales = [str(h) for h in hechos]

    def registrar_paso(self, regla_id: str, regla_nombre: str, 
                       condiciones: list, resultado) -> PasoInferencia:
        """Registra un disparo de regla exitoso."""
        num_paso = len(self.pasos) + 1
        paso = PasoInferencia(
            numero=num_paso,
            regla_id=regla_id,
            regla_nombre=regla_nombre,
            condiciones_cumplidas=condiciones,
            hecho_resultado=str(resultado)
        )
        self.pasos.append(paso)
        return paso

    def registrar_hechos_finales(self, hechos: list):
        """Registra el estado final de la memoria de trabajo al terminar la inferencia."""
        self.hechos_finales = [str(h) for h in hechos]

    def vaciar(self):
        """Reinicia la traza."""
        self.hechos_iniciales.clear()
        self.pasos.clear()
        self.hechos_finales.clear()

    def formatear_markdown(self, seccion_id=None) -> str:
        """Genera un reporte formateado en Markdown de la traza de razonamiento."""
        titulo_seccion = f" en la Sección {seccion_id}" if seccion_id is not None else ""
        
        md = []
        md.append(f"### 🔍 TRAZA DE RAZONAMIENTO DEL SISTEMA EXPERTO{titulo_seccion.upper()}")
        md.append("=" * 60)
        
        # Hechos Iniciales
        md.append("\n**📋 1. Hechos Iniciales (Entrada de Percepción Deep Learning):**")
        if not self.hechos_iniciales:
            md.append("  *Sin hechos iniciales cargados.*")
        else:
            for h in self.hechos_iniciales:
                md.append(f"  - `{h}`")
                
        # Ciclo de Inferencia
        md.append("\n**🧠 2. Ciclo de Inferencia y Disparo de Reglas (Razonamiento Simbólico):**")
        if not self.pasos:
            md.append("  *No se dispararon reglas. Verifique la base de conocimientos.*")
        else:
            for p in self.pasos:
                md.append(f"\n  **Paso {p.numero}: Disparo de Regla `{p.regla_id}` — *\"{p.regla_nombre}\"* **")
                md.append("  * **Condición(es) satisfecha(s):**")
                for cond in p.condiciones_cumplidas:
                    md.append(f"    - `{cond}`")
                md.append(f"  * **Conclusión derivada:** `{p.hecho_resultado}`")
                
        # Hechos Finales / Conclusiones
        md.append("\n**💡 3. Estado Final de la Memoria de Trabajo (Conclusiones Deducidas):**")
        conclusiones = [h for h in self.hechos_finales if h not in self.hechos_iniciales]
        if not conclusiones:
            md.append("  *No se obtuvieron nuevas conclusiones.*")
        else:
            for c in conclusiones:
                md.append(f"  - **`{c}`**")
                
        md.append("\n" + "=" * 60)
        md.append(f"✅ **Estadísticas:** {len(self.pasos)} reglas activadas | {len(self.hechos_finales)} hechos totales en memoria.")
        
        return "\n".join(md)

    def formatear_texto_plano(self, seccion_id=None) -> str:
        """Genera un reporte en texto plano de la traza de razonamiento."""
        titulo_seccion = f" en la Sección {seccion_id}" if seccion_id is not None else ""
        
        lineas = []
        lineas.append(f"🔍 TRAZA DE RAZONAMIENTO — SISTEMA EXPERTO{titulo_seccion.upper()}")
        lineas.append("=" * 60)
        
        lineas.append("📋 Hechos Iniciales:")
        for h in self.hechos_iniciales:
            lineas.append(f"  -> {h}")
            
        lineas.append("\n🧠 Cadena de Inferencia:")
        for p in self.pasos:
            lineas.append(f"  [{p.numero}] REGLA {p.regla_id} disparada: \"{p.regla_nombre}\"")
            lineas.append("      Porque:")
            for cond in p.condiciones_cumplidas:
                lineas.append(f"        - {cond}")
            lineas.append(f"      Resultado: {p.hecho_resultado}")
            
        lineas.append("\n💡 Memoria de Trabajo Final:")
        for h in self.hechos_finales:
            lineas.append(f"  -> {h}")
            
        lineas.append("=" * 60)
        lineas.append(f"Resumen: {len(self.pasos)} reglas activadas | {len(self.hechos_finales)} hechos totales.")
        return "\n".join(lineas)
