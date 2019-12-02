import os
from midi_input import midiToMatrix

def getAllMatrixes(folder_path):
    midi_matrixes = []
    for file in os.listdir(folder_path):
        path = folder_path + "/" + file
        midi_matrix = midiToMatrix(path)
        midi_matrixes.append(midi_matrix)

    return midi_matrixes