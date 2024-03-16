# -*- coding: utf-8 -*-
"""SalimahM_TimeSeries.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1GTBYR5Xea-efaNHQOl1opkLJngzBVBuU

**Membuat Model ML dengan Data Time Series**

*   Nama : Salimah Mahdiyyah
*   Email : salimahdiyyah03@gmail.com
*   Link Dataset : https://www.kaggle.com/datasets/vidhisrivastava/weather-dataset
"""

from google.colab import files
files.upload()

from datetime import datetime, date
from keras.preprocessing.sequence import TimeseriesGenerator
# from keras.models import Sequential, load_model
from sklearn import metrics
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tensorflow as tf
import zipfile
import warnings
warnings.filterwarnings("ignore")

import pandas as pd
df = pd.read_csv('/content/Project1WeatherDataset.csv')
df.head(10)

df.info()

df.isnull().sum()

df['Date/Time']=pd.to_datetime(df['Date/Time'])
df['Date/Time'].head()
df['Temp_C'].fillna(df['Temp_C'].mean(), inplace=True)
df = df[['Date/Time','Temp_C' ]]
df.head()

df.info()

data=df[['Date/Time','Temp_C']].copy()
data['date'] = data['Date/Time'].dt.date

datafinal=data.drop('Date/Time',axis=1)
datafinal.set_index('date', inplace= True)
datafinal.head()

datafinal.info()

import matplotlib.pyplot as plt

plt.figure(figsize=(10,5))
plt.plot(datafinal)
plt.title('Temperature Average', fontsize=20);

train, test = train_test_split(datafinal.values, test_size=0.2, shuffle=False)

scaler = MinMaxScaler()
train_scale = scaler.fit_transform(train.reshape(-1, 1))
test_scale = scaler.fit_transform(test.reshape(-1, 1))

split=int((1-0.2)*len(data))

date_train = data.index[:split]
date_test = data.index[split:]

look_back = 20
train_gen = TimeseriesGenerator(train_scale, train_scale, length=look_back, batch_size=20)
test_gen = TimeseriesGenerator(test_scale, test_scale, length=look_back, batch_size=1)

model_forecast = tf.keras.models.Sequential([
  tf.keras.layers.LSTM(32, activation='relu', return_sequences=True, input_shape=(look_back, 1)),
  tf.keras.layers.GlobalMaxPooling1D(),
  tf.keras.layers.Dropout(0.25),
  tf.keras.layers.Dense(1)
])

model_forecast.summary()

optimizer = tf.keras.optimizers.SGD(lr=1.0000e-04, momentum=0.9)
model_forecast.compile(loss=tf.keras.losses.Huber(), optimizer=optimizer, metrics=["mae"])
model_forecast.fit_generator(train_gen, epochs=10, verbose=1)

pred = scaler.inverse_transform(model_forecast.predict_generator(test_gen))

mae = round(metrics.mean_absolute_error(datafinal.values[split+look_back:],pred), 2)
scale10 = round((datafinal.Temp_C.max() - datafinal.Temp_C.min()) * (10 / 100), 2)

if mae < scale10:
  print("The MAE Score is " + str(mae) + " which is smaller than " + str(scale10) + ". It is a Good Model!")
else:
  print("The MAE Score is " + str(mae) + " which is greater than " + str(scale10) + ". Fix the model again!")

plt.figure(figsize=(20,4))
plt.plot(date_test[:-look_back], test.reshape(-1)[:-look_back], label = "Test Data")
plt.plot(date_test[:-look_back], pred, label = "Prediction based in the Test data")
plt.title('Avg Temperature in C° per {}'.format(data.index.name))
plt.xlabel('{}'.format(data.index.name),fontsize=15)
plt.ylabel('Avg Temperature in C°',fontsize=15)
plt.legend()
plt.show()

optimizer = tf.keras.optimizers.SGD(lr=1.0000e-04, momentum=0.9)
model_forecast.compile(loss='mae', optimizer='adam')
model_forecast.fit_generator(train_gen, epochs=10, verbose=1)