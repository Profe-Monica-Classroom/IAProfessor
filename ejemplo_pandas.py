'''
    Librería pandas para el manejo de grandes cantidades de información
    Esta librería permite realizar análisis de información en archivos CSV
    principalmente (Comma Separated Values).
    
    pip install pandas
    
    Más información de la librería pandas:
        https://pandas.pydata.org/docs/getting_started/index.html
'''
# Importar la librería
import pandas
import matplotlib.pyplot as plt

# Leer los datos de un archivo
# el parámetro index_col = 0, indica que la columna 0 funcionará como el índice
# df = pandas.read_csv('nba.csv', index_col = 0)
df = pandas.read_excel('./muestra_dolar_pib_inflacion_trimestral_categorico.xlsx')

# Ver algunos de los datos leídos (los primeros y últimos)
print(df)

# Tamaño de los datos
df.shape

# Mostrar solo los primeros 5 registros (este número puede cambiar al colocar
# como argumento a .head(n) el número n de datos)
print(df.head())

# Ahora mostrar los últimos 5 datos
print(df.tail())

# Tipos de datos
print(df.dtypes)

# información de los datos
print(df.info())

# ver la estadística de los datos
# conteo, promedio, desviación estándar, mínimo, máximo y cuartiles
print(df.describe())

# Se puede analizar columna de manera individual
df["Mes"]

# Conocer las propiedades estadísticas de los datos de una columna en particular
df["Dolar"].mean()

# O de más de una columna
df[["Mes", "Dolar"]].median()

# Contabilizar el número de datos
df["Mes"].value_counts()

# graficar todos los datos

plt.plot(df['Dolar'], df['Mes'], label='Dolar por mes')
plt.xlabel('Dolar')
plt.ylabel('Mes')
plt.legend()
plt.show()

# Obtener solo datos en específico de una tabla, para crear otra
nueva = df[["Mes", "Dolar", "PIB", "Inflacion"]]
print(nueva)
# Obtener datos específicos de filas
jazz = df[df["Mes"] == "Marzo"]
print(jazz)
# # # # # # # #

x= True
y = False
z = x and not y
print(z)

w = not y
print(w)  
c = x and y
print(c) 

x = 1+2j
y = 3.5 -1j
z = x + y
print(z)
print(type(z))
print(z.real)