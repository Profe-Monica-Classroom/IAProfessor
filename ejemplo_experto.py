import tensorflow as tf

# Define la arquitectura del modelo
model = tf.keras.Sequential()
model.add(tf.keras.layers.Dense(units=32, activation='relu', input_shape=(10,)))
model.add(tf.keras.layers.Dense(units=16, activation='relu'))
model.add(tf.keras.layers.Dense(units=1, activation='sigmoid'))

# Compila el modelo con un optimizador y una función de pérdida
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Entrena el modelo con los datos de entrenamiento
history = model.fit(x_train, y_train, batch_size=32, epochs=10, validation_data=(x_val, y_val))

# Evalúa el modelo con los datos de validación
test_loss, test_acc = model.evaluate(x_test, y_test, verbose=0)
