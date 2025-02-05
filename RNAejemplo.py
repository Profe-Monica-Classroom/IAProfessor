#dataset Fashion MNIST
from tensorflow.keras.datasets import fashion_mnist
# TensorFlow y tf.keras
import tensorflow as tf
from tensorflow import keras
from keras import optimizers

from sklearn.model_selection import train_test_split

# Librerias de ayuda
import numpy as np
import matplotlib.pyplot as plt

(X, y), (X_test, y_test) = fashion_mnist.load_data()

# Cargamos los labels del dataset.
labels = ["T-shirt/top",
          "Trouser",
          "Pullover",
          "Dress",
          "Coat",
          "Sandal",
          "Shirt",
          "Sneaker",
          "Bag",
          "Ankle boot"]

# Mostramos una tabla con las algunas imagenes del dataset
plt.figure(figsize=(14,8))
ind = np.random.choice(X.shape[0],20)
for i,img in enumerate(ind):
    plt.subplot(5,10,i+1)
    plt.title(labels[y[img]])
    plt.imshow(X[img], cmap="binary")
    plt.axis("off")

#PREPARANDO DATASET

# Dividimos el dataset en dos partes 10% de las imagenes totales serán para testeo y el 90% restante para entrenamiento
X_train, X_test, y_train, y_test = train_test_split(X,y, test_size=0.1)
print("Imágenes de entrenamiento", X_train.shape)
print("Imágenes de test", X_test.shape)

#LA RED NEURONAL

model = keras.Sequential([
    keras.layers.Flatten(input_shape=(28, 28)),
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dense(10, activation='softmax')
])


# Configuramos como se entrenará la red
model.compile(
    loss="sparse_categorical_crossentropy",
    optimizer=keras.optimizers.RMSprop(learning_rate=0.001), 
    metrics=["accuracy"]
)

# Definimos los parametros de entrenamiento
params = {
    "validation_data": (X_train,y_train),
    "epochs": 100,
    "verbose": 2,
    "batch_size":256,
}

# Iniciamos el entrenamiento
entrenamiento = model.fit(X_train,y_train,**params)
model.save('RNAejemplo.h5') # para guardar el modelo entrenado

plt.xlabel('Ciclos de Entrenamiento')
plt.ylabel('Errores')
plt.plot(entrenamiento.history['loss'])
plt.show()

#x=np.arange(-5,5,0.05)
#y=np.cos(x)

#plt.plot(x,y)
#plt.show()

#EVALUANDO EL MODELO

model.evaluate(X_test,y_test)

history = model.fit(X_train, y_train, epochs=10, batch_size=10, validation_split=0.2, verbose=0)

y_pred = model.predict(X_test)

score = model.evaluate(X_test, y_test, verbose=0)
print('Error Medio Cuadratico:', score[1])

#Imprimir el resultado de la prediccion

print(y_pred)