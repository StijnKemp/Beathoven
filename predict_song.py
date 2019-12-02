from midi_input import midiToMatrix, generateTestNetworkInputs

import globals
import time
import glob
import random
from keras.models import model_from_json


from midi_output import networkOutToMatrix, matrixToMidi

def predict(test_data):
    
    file_name = 'Beathoven_%s.mid' %(time.strftime("%Y%m%d_%H_%M"))
    folder_path = '%s%s' %(globals.generated_midi_directory, file_name)

    for i, song in enumerate(test_data):
        network_output = network.predict(song)

        # convert all songs into matrixes
        network_matrix = networkOutToMatrix(network_output)
        # convert all matrixes to midi
        matrixToMidi(network_matrix, folder_path)


def run(folder_path):
    initialize()

    midi_files = glob.glob(folder_path + '/*.mid')

    #choose a random file as a primer
    file_idx = random.randint(0,len(midi_files) - 1)
    primer = midi_files[file_idx]
    test_piano_roll = midiToMatrix(primer)
    test_data = [test_piano_roll]
    test_input = generateTestNetworkInputs(test_data, globals.x_sequence_length)
    
    predict(test_input)

def initialize():
    global network

    network = model_from_json(open(globals.model_directory).read())
    network.load_weigth(globals.weights_directory)
    network.compile(loss = globals.loss_function, optimizer=globals.optimizer) 
