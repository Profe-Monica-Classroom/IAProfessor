"""
### **Agente de Inventario en Python**
 **Métodos:**
   - **`calcular_utilidad(producto)`**:
     - Calcula la utilidad de un producto en función de su nivel de inventario.
     - Si el nivel actual está por debajo del nivel óptimo, se penaliza con un valor negativo proporcional al déficit.
     - Si el nivel actual está por encima del nivel óptimo, se penaliza con un valor negativo menor proporcional al exceso.
     - Si el nivel actual coincide con el nivel óptimo, se asigna una alta utilidad (valor positivo).

   - **`revisar_inventario()`**:
     - Recorre todos los productos definidos en los niveles óptimos.
     - Calcula la utilidad de cada producto usando el método `calcular_utilidad`.
     - Toma decisiones basadas en la utilidad:
       - Si la utilidad es negativa y el nivel actual está por debajo del óptimo, decide "Reabastecer".
       - Si la utilidad es negativa y el nivel actual está por encima del óptimo, decide "Reducir inventario".
       - Si la utilidad es positiva, decide "Mantener nivel actual".
     - Devuelve un diccionario con las decisiones para cada producto.

    print("Decisiones del agente de inventario:")
    for producto, decision in decisiones.items():
        print(f"{producto}: {decision}")    
"""


class AgenteInventario:
    def __init__(self, inventario, niveles_optimos):
        """
        Inicializa el agente con el inventario actual y los niveles óptimos.
        :param inventario: Diccionario con productos y sus cantidades actuales.
        :param niveles_optimos: Diccionario con productos y sus niveles óptimos.
        """
        self.inventario = inventario
        self.niveles_optimos = niveles_optimos

    def calcular_utilidad(self, producto):
        """
        Calcula la utilidad para un producto basado en su nivel de inventario.
        :param producto: Nombre del producto.
        :return: Valor de utilidad (positivo si está en nivel óptimo, negativo si no).
        """
        cantidad_actual = self.inventario.get(producto, 0)
        nivel_optimo = self.niveles_optimos.get(producto, 0)
        if cantidad_actual < nivel_optimo:
            valor = -1 * (nivel_optimo - cantidad_actual)
            print(valor)
            return -1 * (nivel_optimo - cantidad_actual)  # Penalización por déficit
        elif cantidad_actual > nivel_optimo:
            valor2 = -0.5 * (cantidad_actual - nivel_optimo)
            print(valor2)
            return -0.5 * (cantidad_actual - nivel_optimo)  # Penalización por exceso
        else:
            return 10  # Alta utilidad si está en el nivel óptimo

    def revisar_inventario(self):
        """
        Revisa el inventario y toma decisiones basadas en la utilidad.
        """
        decisiones = {}
        for producto in self.niveles_optimos.keys():
            utilidad = self.calcular_utilidad(producto)
            if utilidad < 0:
                if self.inventario.get(producto, 0) < self.niveles_optimos[producto]:
                    decisiones[producto] = "Reabastecer"
                else:
                    decisiones[producto] = "Reducir inventario"
            else:
                decisiones[producto] = "Mantener nivel actual"
        return decisiones


# Ejemplo de uso
if __name__ == "__main__":
    inventario_actual = {
        "manzanas": 25,
        "naranjas": 40,
        "bananas": 15
    }

    niveles_optimos = {
        "manzanas": 40,
        "naranjas": 30,
        "bananas": 15
    }

    agente = AgenteInventario(inventario_actual, niveles_optimos)
    decisiones = agente.revisar_inventario()

    print("Decisiones del agente:")
    for producto, decision in decisiones.items():
        print(f"{producto}: {decision}")