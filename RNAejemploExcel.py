import pandas as pd #para maniipular entradas de datos como datasets
from pandas import DataFrame # Para utilizar el metodo DataFrame del modulo Pandas
from keras.models import Sequential # para hacer el modelo de la red neuronal
from keras.layers import Dense # para manejar la cantidad de capas y de neuronas
import numpy as np # libreria o modulo para manipulacion de fechas y numeros
from sklearn.model_selection import train_test_split # dividir datos y crean conjuntos de datos de training y testing
from sklearn.preprocessing import StandardScaler # para escalar datos numericos a datos decimales

# Fija las semillas aleatorias para la red neuronal
np.random.seed(4)

#Leyendo las columnas y la data
df = pd.read_excel('./muestra_dolar_pib_inflacion_trimestral_categorico.xlsx')
print(df)
df = DataFrame(df, columns=['Mes_number','Dolar','PIB','Inflacion'])
print(df)

X = df #df.drop(['Mes_number', 'Dolar', 'PIB', 'Inflacion'], axis=1).values
print(X)
print(X.shape)

# Obtener las etiquetas para cada una de las cuatro salidas
y1 = np.float32(df['Mes_number'].values)
y2 = df['Dolar'].values
y3 = df['PIB'].values
y4 = df['Inflacion'].values
print([y1,y2,y3,y4])


#Se definen los conjuntos de datos de entrenamiento
X_train, X_test = train_test_split(X, test_size=0.2, random_state=4)

print(X_train)
print(X_test)

y1_train, y1_test = train_test_split(y1, test_size=0.2)#, random_state=4)
y2_train, y2_test = train_test_split(y2, test_size=0.2)
y3_train, y3_test = train_test_split(y3, test_size=0.2)
y4_train, y4_test = train_test_split(y4, test_size=0.2)


# Normalizar los datos de entrada y salida
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
print(X_train)
X_test = scaler.transform(X_test)
print(X_test)

y1_train = scaler.fit_transform(y1_train.reshape(-1, 1))
y2_train = scaler.fit_transform(y2_train.reshape(-1, 1))
y3_train = scaler.fit_transform(y3_train.reshape(-1, 1))
y4_train = scaler.fit_transform(y4_train.reshape(-1, 1))

print(y1_train, y2_train, y3_train, y4_train)

y1_test = scaler.transform(y1_test.reshape(-1, 1))
y2_test = scaler.transform(y2_test.reshape(-1, 1))
y3_test = scaler.transform(y3_test.reshape(-1, 1))
y4_test = scaler.transform(y4_test.reshape(-1, 1))
print(y1_test, y2_test, y3_test, y4_test)


model = Sequential()
model.add(Dense(12, input_dim=4, activation='relu')) # capa de entrada
model.add(Dense(8, activation='relu')) #capa oculta
model.add(Dense(1, activation='sigmoid')) # capa de salida


# Compilar y ajustar el modelo
model.compile(loss='mse', optimizer='adam', metrics=['mse'])

history = model.fit(X_train, y2_train, epochs=150, batch_size=10, validation_split=0.2, verbose=0) # entrenamiento de la red neuronal

y2_pred = model.predict(X_test)

#Evaluamos la prediccion del modelo
score = model.evaluate(X_test, y2_test, verbose=0)
print('Error Medio Cuadratico:', score[1])

#Predicciones

y2_pred_scaled = model.predict(X_test)
y2_pred = scaler.inverse_transform(y2_pred_scaled)

#Meses del Año

meses_test = X_test[:, 0] / 12


import matplotlib.pyplot as plt # Es Necesaria para graficar

plt.plot(meses_test, y2_test, label='Datos de prueba')
plt.xlabel('Años')
plt.ylabel('Valor de la primera salida')
plt.legend()
plt.show()


plt.plot(meses_test, y2_pred, label='Predicción')
plt.xlabel('Años')
plt.ylabel('Valor de la primera salida')
plt.legend()
plt.show()

#Otra forma

import calendar #Para trabajar fechas en series de tiempo

# Lista de los nombres de los meses
meses_nombres = list(calendar.month_name)[1:]
print(meses_nombres)
y2_pred = model.predict(X_test)
y2_pred = np.squeeze(y2_pred)
#y2_test = scaler.inverse_transform(y2_test)

y2_test = np.squeeze(y2_test)
# Crear una serie de tiempo con las predicciones y los nombres de los meses
y2_pred_serie = pd.Series(y2_pred.squeeze(), index=pd.date_range(start='9/1/2019', periods=len(y2_pred), freq='M'))
y2_test_serie = pd.Series(y2_test.squeeze(), index=pd.date_range(start='9/1/2019', periods=len(y2_test), freq='M'))

# Crear el gráfico con los nombres de los meses en el eje x
plt.plot( y2_test_serie, label='Datos de prueba')
plt.xlabel('Meses')
plt.ylabel('Valor de la primera salida')
plt.legend()
plt.show()


plt.plot( y2_pred_serie, label='Predicción')
plt.xlabel('Meses')
plt.ylabel('Valor de la primera salida')
plt.legend()
plt.show()

#Imprimiendo la red neuronal

from keras.utils import plot_model

plot_model(model, to_file='red_neuronal.png', show_shapes=True, show_layer_names=True)
