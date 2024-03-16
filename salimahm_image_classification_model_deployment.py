# -*- coding: utf-8 -*-
"""SalimahM_Image Classification Model Deployment.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1r_KQLm60vFfjF7jczlnfQDVRs78js_Go

Image Classification Model Deployment


---


*   Nama : Salimah Mahdiyyah
*   Email : salimahdiyyah03@gmail.com
*   Link Dataset : https://www.kaggle.com/datasets/vencerlanz09/reptiles-and-amphibians-image-dataset/data
"""

!pip install kaggle

from google.colab import files

files.upload()

!mkdir -p ~/.kaggle
!cp kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json

!kaggle datasets download -d vencerlanz09/reptiles-and-amphibians-image-dataset -p /content/reptiles

!unzip /content/reptiles/reptiles-and-amphibians-image-dataset.zip -d /content/reptiles

!ls /content/reptiles

import os
reptiles = os.path.join('/content/reptiles')
print(os.listdir(reptiles))

from tensorflow.keras.preprocessing.image import ImageDataGenerator
train_datagen = ImageDataGenerator(rescale=1./255,
    zoom_range=0.2,
    shear_range=0.2,
    rotation_range=20,
    fill_mode='nearest',
    horizontal_flip=True,
    validation_split=0.2)

train_generator = train_datagen.flow_from_directory(
      reptiles,
      target_size=(224, 224),
      batch_size=64,
      classes=['Salamander', 'Lizard', 'Crocodile_Alligator'],
      class_mode='categorical',
      subset='training')
validation_generator = train_datagen.flow_from_directory(
      reptiles,
      target_size=(224, 224),
      batch_size=64,
      classes=['Salamander', 'Lizard', 'Crocodile_Alligator'],
      class_mode='categorical',
      subset='validation')

from keras.applications.vgg16 import VGG16
from tensorflow.keras.layers import Input
base_model = VGG16(include_top=False, input_tensor=Input(shape=(224, 224, 3)))
base_model.trainable = False
base_model.summary()

import tensorflow as tf
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.regularizers import l2

model = tf.keras.models.Sequential([
    base_model,
    # Flatten the results to feed into a DNN
    tf.keras.layers.Flatten(),
    # 512 neuron hidden layer
    tf.keras.layers.Dense(512, activation='relu'),
    tf.keras.layers.Dropout(0.4),
    tf.keras.layers.Dense(256, activation='relu'),
    tf.keras.layers.Dense(3, activation='softmax')
])

model.compile(optimizer=tf.optimizers.Adam(),
              loss='categorical_crossentropy',
              metrics = ['accuracy'])
model.summary()

class myCallback(tf.keras.callbacks.Callback):
   def on_epoch_end(self, epoch, logs={}):
      if(logs.get('accuracy') >= 0.85 and logs.get('val_accuracy') >= 0.85):
          print("\nAkurasi 85%, training end!!")
          self.model.stop_training = True
callbacks = myCallback()

reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(monitor='val_loss', patience=15, min_lr=0.00001, verbose=2)

with tf.device('/device:GPU:0'):
  history = model.fit(train_generator,
                   validation_data=validation_generator,
                   epochs=500,
                   batch_size=128,
                   callbacks=[callbacks, reduce_lr],
                   steps_per_epoch=5,
                   verbose=2)

import numpy as np
import matplotlib.pyplot as plt
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('Accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='upper left')
plt.show()

plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('Loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'val'], loc='upper left')
plt.show()

export_dir = 'saved_model/'
tf.saved_model.save(model, export_dir)

converter = tf.lite.TFLiteConverter.from_saved_model(export_dir)
tflite_model = converter.convert()

import pathlib

tflite_model_file = pathlib.Path('reptiles.tflite')
tflite_model_file.write_bytes(tflite_model)