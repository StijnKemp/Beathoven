from keras.models import Sequential
from keras.layers.recurrent import LSTM
from keras.layers.normalization import *
from keras.layers import TimeDistributed
from keras.layers.core import *
from keras.models import model_from_json
from keras.callbacks import EarlyStopping, History

import globals 
from utility import getAllMatrixes
from midi_input import generateNetworkInputs

import time
import sys
import os
import numpy as np

# parameters
num_neurons = 64
batch_size = 64
epochs = 100 # edit this!

def createNetwork():
    # create initial encoder layer
    network = Sequential()
    network.add(LSTM(input_dim = globals.input_dimension, output_dim = num_neurons, activation= 'tanh', return_sequences = True))
    network.add(BatchNormalization())
    network.add(Dropout(0.3))
    # add conncetion layer from input to next layer
    network.add(LSTM(num_neurons, activation= 'tanh'))

    # add decoder layers
    network.add(RepeatVector(globals.y_sequence_length))
    num_layers= 2
    for _ in range(num_layers):
        network.add(LSTM(num_neurons, activation= 'tanh', return_sequences = True))
        network.add(BatchNormalization())
        network.add(Dropout(0.3))

    # add output layer
    network.add(TimeDistributed(Dense(globals.output_dimension, activation= 'softmax')))
	
    return network

def train(folder_path):
    midi_matrixes = getAllMatrixes(folder_path)
    input_matrix, target_matrix = generateNetworkInputs(midi_matrixes, globals.x_sequence_length, globals.y_sequence_length)
    # convert matrixes to bools for keras efficiency
    input_matrix = input_matrix.astype(np.bool)
    target_matrix = target_matrix.astype(np.bool)

    network = createNetwork()
    # for checking network parameters
    #model.summary
    network.compile(loss = globals.loss_function, optimzer = globals.optimizer)
    #use early stop to prevent overfitting
    earlystop = EarlyStopping(monitor='loss', patience= 10, min_delta = 0.01 , verbose=0, mode= 'auto')

    # where the magic happens!
    history = network.fit(input_matrix, target_matrix, batch_size = batch_size, nb_epoch = epochs, callbacks = [ earlystop, History() ])

    # save weights
    weights_file = 'Beathoven_weights_%d_epochs_%s' %(epochs, time.strftime("%Y%m%d_%H_%M"))
    weights_path = '%s/%s' %(globals.weights_directory, weights_file)
    network.save_weights(weights_path)

    # save model
    model_file = 'Beathoven_model_%s' %(time.strftime("%Y%m%d_%H_%M"))
    model_path = '%s/%s' %(globals.model_directory, model_file)
    json_string = network.to_json()
    open(model_path, 'w').write(json_string)