###############################################################
# Autor: Ing. Monica Tahan
# Script para Análisis Financiero con Arbol de Decision
# Fecha: 20/02/2024
# Version:1.0
###############################################################
# Cargando las librerias:

import pandas as pd #nos permite formatear datasets
from sklearn.tree import DecisionTreeRegressor # nos permite generar un modelo de arbol
from sklearn.metrics import mean_squared_error # para evaluar el error medio cuadratico
from pandas import DataFrame #para crear los dataframes
import matplotlib.pyplot as plt

import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeRegressor, export_graphviz

# Fija las semillas aleatorias para el arbol de decision
np.random.seed(4)

#Leyendo las columnas y la data
df = pd.read_excel('./muestra_dolar_pib_inflacion_trimestral_categorico.xlsx')
print(df)
df = DataFrame(df, columns=['Mes_number','Dolar','PIB','Inflacion'])
print(df)


train_size = int(len(df) * 0.8) # 80% de la muestra para entrenamiento
print(train_size)
train_data, test_data = df[:train_size], df[train_size:]

print(len(train_data))
print(len(test_data))

print(train_data)
print(test_data)
# Definir las columnas de entrada y salida
input_cols = ['Mes_number', 'Dolar', 'PIB']
print(input_cols)
output_cols = ['Inflacion']

#Creamos el arbol de decision
tree_model = DecisionTreeRegressor(random_state=0)

#Entrenamos el arbol

tree_model.fit(train_data[input_cols], train_data[output_cols])

# Hacer predicciones sobre los datos de prueba
y_pred = tree_model.predict(test_data[input_cols])

# Calcular el error cuadrático medio de las predicciones
mse = mean_squared_error(test_data[output_cols], y_pred)

# Imprimir el error cuadrático medio
print("Error cuadrático medio:", mse)

#Imprimiendo Prediccion

print("Predicción:", y_pred)

# Exportar el árbol de decisión a formato .dot
export_graphviz(tree_model, out_file='tree.dot', feature_names=input_cols)



# Convertir el archivo .dot a formato PNG (requiere Graphviz)
#dot -Tpng tree.dot -o tree.png

#Imprimir resultados prediccion segun el dolar

plt.plot(test_data['Dolar'], y_pred, label='Datos de prueba')
plt.xlabel('Dolar')
plt.ylabel('Inflacion')
plt.legend()
plt.show()


#Imprimir resultados prediccion segun el dolar

plt.plot(test_data['PIB'], y_pred, label='Datos de prueba')
plt.xlabel('PIB')
plt.ylabel('Inflacion')
plt.legend()
plt.show()

# Imprimir resultados prediccion tri mensual

plt.plot(test_data['Mes_number'], y_pred, label='Datos de prueba')
plt.xlabel('Mes_number')
plt.ylabel('Inflacion')
plt.legend()
plt.show()