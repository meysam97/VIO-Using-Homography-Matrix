#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr 24 14:26:34 2022

@author: Meysam
"""

import numpy as np
import pandas as pd
from keras.layers import (Conv2D, Dense, Input, LeakyReLU, 
                          Bidirectional, LSTM, Flatten, concatenate, 
                          Multiply, Dropout, TimeDistributed, Reshape, 
                          GlobalMaxPool2D, BatchNormalization)
from tensorflow.keras.utils import plot_model
from keras.callbacks import ModelCheckpoint, Callback
import matplotlib.pyplot as plt
from keras import regularizers
from tensorflow.keras import initializers
from keras import Model
import tensorflow as tf
from sklearn import preprocessing
from trajectory_plotter import trajectory_plotter
from sklearn.metrics import mean_squared_error, mean_absolute_error
from sklearn.model_selection import train_test_split
import  os
# In[] load data


cdir = os.getcwd()
pose = np.array(pd.read_csv(cdir + '/dataset_csv/pose.csv'))
pose = pose[:,1:]
imu = np.array(pd.read_csv(cdir + '/dataset_csv/imu.csv'))
imu = imu[:,1:]
H = np.array(pd.read_csv(cdir + '/dataset_csv/homography_matrixes.csv'))
H = H[:,1:]





X = imu
scaler_x = preprocessing.StandardScaler().fit(X)
X = scaler_x.transform(X)
y = pose[:,:3]



# In[] train-test split



X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=5)

# In[ MODEL]

l2_value = 1e-5
dropout_ratio = 0.05

input_1 = Input(shape=(X.shape[1],), name='homography matrix')
x = Dense(128,
          kernel_initializer=tf.keras.initializers.RandomNormal(mean=0., stddev=0.05),
          kernel_regularizer=regularizers.L2(l2_value),
          activation='relu')(input_1)
x = BatchNormalization()(x)
x = Dropout(dropout_ratio)(x)
x = Dense(128, activation='relu', 
          kernel_initializer=tf.keras.initializers.RandomNormal(mean=0., stddev=0.05),
          kernel_regularizer=regularizers.L2(l2_value))(x)
x = BatchNormalization()(x)
x = Dropout(dropout_ratio)(x)
x = Dense(256, activation='relu', 
          kernel_initializer=tf.keras.initializers.RandomNormal(mean=0., stddev=0.05),
          kernel_regularizer=regularizers.L2(l2_value))(x)
x = BatchNormalization()(x)
x = Dropout(dropout_ratio)(x)
x = Dense(256, activation='relu', 
          kernel_initializer=tf.keras.initializers.RandomNormal(mean=0., stddev=0.05),
          kernel_regularizer=regularizers.L2(l2_value))(x)
x = BatchNormalization()(x)
x = Dropout(dropout_ratio)(x)
x = Dense(256, activation='relu', 
          kernel_initializer=tf.keras.initializers.RandomNormal(mean=0., stddev=0.05),
          kernel_regularizer=regularizers.L2(l2_value))(x)
x = BatchNormalization()(x)
x = Dropout(dropout_ratio)(x)
x = Dense(256, activation='relu', 
          kernel_initializer=tf.keras.initializers.RandomNormal(mean=0., stddev=0.05),
          kernel_regularizer=regularizers.L2(l2_value))(x)
x = BatchNormalization()(x)
x = Dropout(dropout_ratio)(x)
x_concat = Dense(128, activation='relu', 
                  kernel_initializer=tf.keras.initializers.RandomNormal(mean=0., stddev=0.05),
                  kernel_regularizer=regularizers.L2(l2_value))(x)
# x_concat = BatchNormalization()(x)
# x_concat = Dropout(dropout_ratio)(x)
x = Dense(units=128, activation='relu', 
          kernel_initializer=tf.keras.initializers.RandomNormal(mean=0., stddev=0.05),
          kernel_regularizer=regularizers.L2(l2_value))(x_concat)
# X = BatchNormalization()(x)
x = Multiply()([x_concat, x])
x = BatchNormalization()(x)
x = Dropout(dropout_ratio)(x)
x = Dense(64,
          kernel_initializer=tf.keras.initializers.RandomNormal(mean=0., stddev=0.05),
          activation='relu', 
          kernel_regularizer=regularizers.L2(l2_value))(x)
# x = BatchNormalization()(x)
outputs = Dense(3, name='pose')(x)

model = Model(input_1, outputs)




model.summary()
plot_model(model, show_layer_names=True, show_shapes=True, dpi=300)


lr_schedule = tf.keras.optimizers.schedules.ExponentialDecay(initial_learning_rate=1e-3,
                                                             decay_steps=1000,
                                                             decay_rate=0.93)


reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(monitor='loss',
                                     factor=0.7,
                                     patience=4,
                                     verbose=1,
                                     cooldown=0,
                                     min_lr=1e-6)


model.compile(tf.keras.optimizers.Adam(learning_rate=1e-3), 
                  loss=tf.keras.losses.MeanAbsoluteError(),
                  # loss_weights = [0.1,0.1,0.8],
                  metrics=[tf.keras.losses.MeanAbsoluteError()])



model_history = model.fit(x=X_train, 
                          y=y_train,
                          batch_size=128,
                          # class_weight={0:3.0, 1:3.0, 2:1.0},
                          # validation_split=0.2,
                               validation_data=(X_test, y_test), 
                              epochs=250,
                              verbose=1,
                               callbacks=[reduce_lr],
                              validation_freq=1, shuffle=True,
                              workers=8)






plt.figure(dpi=300)
plt.plot(model_history.history['val_loss'])
plt.plot(model_history.history['loss'])
plt.title('Training loss and validation loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['val loss', 'train loss'], loc='upper right')
plt.show()







mae_train = mean_absolute_error(y_train, model.predict(X_train))
mae_test = mean_absolute_error(y_test, model.predict(X_test))
print("MAE train: {:.4f}".format(mae_train))
print("MAE test: {:.4f}".format(mae_test))


X = imu
scaler_x = preprocessing.StandardScaler().fit(X)
X = scaler_x.transform(X)
trajectory_plotter(model.predict(X), y)














