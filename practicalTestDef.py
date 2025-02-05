# #####################################################
# Author: Monica Tahan. monicatahan@gmail.com.  YouTube Channel: http://www.youtube.com/monicatahan 
# Perfil Linkedin: https://www.linkedin.com/in/monicatahan/
# FACE PROCESSING WITH PYTHON
# VERSION 1.0
# USED METHOD: TENSORFLOW FOR IMAGES, USING TENSORFLOW OFFICIAL DOCUMENTATION
# REFERENCES: https://www.tensorflow.org/tutorials/images/classification
#  
# -----------------------------------------------------

## --------------------------------------------------#
#               NOTES                                #
##---------------------------------------------------#
# I did this code considering the official           #
# recomending of TensorFlow, but really when you are #
# training a model for age range detection you have  #
# to write the code considering hybrids techiniques  #
# for example, mobilenet training for age and Sex,   #
# boxing each faces into the training to generate    #
# your model.                                        #
#  PLEASE READ ALL COMMENTS AROUND THIS SCRIPT       #
#----------------------------------------------------#

##----------------------------------------------------#
# IMPORTING NEEDED MODULES                            #
#-----------------------------------------------------#

import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential
import cv2
import numpy as np
import matplotlib.pyplot as plt
import os
import PIL
import pathlib


##---------------------------------------##
# IMPORTING DATASET 1INFLUENCERS          #
#-----------------------------------------#

# Making dataset path

dataset_url = "https://prueba.virtualunexpo.com/pruebaIA/dataset.tgz"
data_dir = tf.keras.utils.get_file('dataset', origin=dataset_url, untar=True)
data_dir = pathlib.Path(data_dir)

# Counting images to validate download
image_count = len(list(data_dir.glob("*/*.jpg")))
print(image_count) # the dataset has 527 jpg files

#Let it see 1 photo 0-2
twoy = list(data_dir.glob('0-2/*'))
PIL.Image.open(str(twoy[1])) 


# Making a dataset for next training and model creation

batch_size = 32
img_height = 180
img_width = 180
#------------------------------------------------------------#
# DEFINING THE MODELS AND TRAINING PARAMETERS: CASE 80% 20%  #
#------------------------------------------------------------#

# To read the images I'll use image_dataset_from_directory to use the image directory for training

train_ds = tf.keras.utils.image_dataset_from_directory(
  data_dir,
  validation_split=0.4, # PLEASE FOR TRAINING 70% CRITE HERE 0.3 AND 60% USE 0.4
  subset="training",
  seed=128,
  image_size=(img_height, img_width),
  batch_size=batch_size)

val_ds = tf.keras.utils.image_dataset_from_directory(
  data_dir,
  validation_split=0.4, # PLEASE FOR TRAINING 70% CRITE HERE 0.3 AND 60% USE 0.4
  subset="validation",
  seed=128,
  image_size=(img_height, img_width),
  batch_size=batch_size)

class_names = train_ds.class_names
print(class_names)

  #------------------------------------------------------#
# IF YOU WANT TO SEE THE FIRST 9 TRAINING MODEL IMAGE #
#------------------------------------------------------#
plt.figure(figsize=(10, 10)) # TO print 9 images with 10px of weight and 10 pixels of high


for images, labels in train_ds.take(1):
  for i in range(9):
    ax = plt.subplot(3, 3, i + 1)
    plt.imshow(images[i].numpy().astype("uint8"))
    plt.title(class_names[labels[i]])
    plt.axis("off")

#-------------------------------------------------------------#
#  TRAINING MODEL USING image_bath with train_ds model        #
# The last dimenion is about RGB Color                        #
#-------------------------------------------------------------#

for image_batch, labels_batch in train_ds:
  print(image_batch.shape)
  print(labels_batch.shape)
  break

# ------------------------------------------------------#
# AUTOTUNE CACHE AND PREFETCH FOR THE BEST PERFORMANCE  #
#-------------------------------------------------------#

AUTOTUNE = tf.data.AUTOTUNE
train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=AUTOTUNE)
val_ds = val_ds.cache().prefetch(buffer_size=AUTOTUNE)

#--------------------------------------------------------#
# NOW, when you are going to train using Neural Networks #
# You have to normalize the data for the best            #
# performance of your processor and your GPU, because    #
# Neural Network needs little values                     #
#--------------------------------------------------------#
normalization_layer = layers.Rescaling(1./255)

normalized_dataset = train_ds.map(lambda x, y: (normalization_layer(x), y))
image_batch, labels_batch = next(iter(normalized_dataset))
first_image = image_batch[0]

# Notice the pixel values are now in [0,1].
print(np.min(first_image), np.max(first_image))

num_classes = len(class_names)
print(num_classes)

#---------------------------------------------------------#
# CREATING SEQUENTIAL MODEL:                              #
#---------------------------------------------------------#
# In this example i applied sequential model to show as   #
# tensorflow works with 2D convolution using 3 blocks:    #
# Con2D, MaxPooling2D and Dense                           #
# For a classification with a better precision, I suggest #
# use a training model with MobilNet, for a high precision#
#---------------------------------------------------------#

model = Sequential([
  layers.Rescaling(1./255, input_shape=(img_height, img_width, 3)),
  layers.Conv2D(16, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Conv2D(32, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Conv2D(64, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Flatten(),
  layers.Dense(128, activation='relu'),
  layers.Dense(num_classes)
])

#----------------------------------------------------#
# COMPILING MODEL                                    #
#----------------------------------------------------#
model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])
#----------------------------------------------------#
# NUM OF ITERATIONS TRAINING THE MODEL               #
#----------------------------------------------------#
epochs=20
history = model.fit(
  train_ds,
  validation_data=val_ds,
  epochs=epochs
)

#-----------------------------------------------------#
# MODEL ACCURACY                                      #
#-----------------------------------------------------#
acc = history.history['accuracy']
val_acc = history.history['val_accuracy']

loss = history.history['loss']
val_loss = history.history['val_loss']

epochs_range = range(epochs)

plt.figure(figsize=(8, 8))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Training Accuracy')
plt.plot(epochs_range, val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.plot(epochs_range, val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.show()

#------------------------------------------------------------#
# IT IS VERY PROBABLE MODEL OVERFITTING                      #
# In this model, accuracy is over 56%, during the training   #
# process. In this case I adjusted trough data augmentation  #
# as TensorFlow Official Tutorial suggest                    #
#------------------------------------------------------------#

data_augmentation = keras.Sequential(
  [
    layers.RandomFlip("horizontal",
                      input_shape=(img_height,
                                  img_width,
                                  3)),
    layers.RandomRotation(0.1),
    layers.RandomZoom(0.1),
  ]
)

plt.figure(figsize=(10, 10))

for images, _ in train_ds.take(1):
  for i in range(9):
    augmented_images = data_augmentation(images)
    ax = plt.subplot(3, 3, i + 1)
    plt.imshow(augmented_images[0].numpy().astype("uint8"))
    plt.axis("off")

plt.show()

num_classes = len(class_names)
print(num_classes)

#----------------------------------------------------------#
# I also wanted to try dropout regilarization              #
# using the data augmentation                              #
#----------------------------------------------------------#
model = Sequential([
  data_augmentation,
  layers.Rescaling(1./255),
  layers.Conv2D(16, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Conv2D(32, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Conv2D(64, 3, padding='same', activation='relu'),
  layers.MaxPooling2D(),
  layers.Dropout(0.2),
  layers.Flatten(),
  layers.Dense(128, activation='relu'),
  layers.Dense(num_classes)
])

# -----------------------------------------------------------#
# Compiling and training the model AGAIN                     #
#------------------------------------------------------------#

model.compile(optimizer='adam',
              loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
              metrics=['accuracy'])

model.summary()

epochs = 40
history = model.fit(
  train_ds,
  validation_data=val_ds,
  epochs=epochs
)

acc = history.history['accuracy']
val_acc = history.history['val_accuracy']

loss = history.history['loss']
val_loss = history.history['val_loss']

epochs_range = range(epochs)

#--------------------------------------------------------#
# SHOWING TRAINING RESULTS                               #
#--------------------------------------------------------#

plt.figure(figsize=(8, 8))
plt.subplot(1, 2, 1)
plt.plot(epochs_range, acc, label='Training Accuracy')
plt.plot(epochs_range, val_acc, label='Validation Accuracy')
plt.legend(loc='lower right')
plt.title('Training and Validation Accuracy')

plt.subplot(1, 2, 2)
plt.plot(epochs_range, loss, label='Training Loss')
plt.plot(epochs_range, val_loss, label='Validation Loss')
plt.legend(loc='upper right')
plt.title('Training and Validation Loss')
plt.show()

#---------------------------------------------------------#
# MAKING A PREDICTION WITH SOME IMAGES                    #
#---------------------------------------------------------#

imageTest_url = "https://prueba.virtualunexpo.com/pruebaIA/imagen_prueba3.jpg"
imageTest_path = tf.keras.utils.get_file('imagen_prueba3', origin=imageTest_url)

img = tf.keras.utils.load_img(
    imageTest_path, target_size=(img_height, img_width)
)
img_array = tf.keras.utils.img_to_array(img)
img_array = tf.expand_dims(img_array, 0) # Create a batch

predictions = model.predict(img_array)
score = tf.nn.softmax(predictions[0])

print(
    "This image most likely belongs to {} age range with a {:.2f} percent of confidence."
    .format(class_names[np.argmax(score)], 100 * np.max(score))
)

