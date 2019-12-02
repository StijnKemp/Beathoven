import numpy as np
import mido as m
from math import ceil
import globals
from sklearn.utils import shuffle

np.set_printoptions(edgeitems=1000000)

def midiToMatrix(path):
    # use Mido constructor to convert midi file to array with
    # midi_data = m.MidiFile(path)
    #   ticks_per_beat = 960, can differ per file
    midi_data = m.MidiFile('C:\dev\school\minor_ai\minor_ai_repo\Beathoven2.4\midi\scale_a_aeolian.mid')
    ticks_per_beat = midi_data.ticks_per_beat

    # tempo_events :
    #   message : set_tempo
    #   tempo = 500000 = 120 BPM
    #   time = 0
    tempo_events = [x for t in midi_data.tracks for x in t if str(x.type) == 'set_tempo']

    # convert microseconds to bpm
    # 60000000 / 500000 = 120
    # microseconds_per_minute = 60000000
    tempo = tempo_events[0].tempo
    bpm = globals.microseconds_per_minute / tempo

    #time_slice = 0.02 # 200ms for each column in piano roll
    # (960 * 120 * 0.02) / 60 = 38.5
    ticks_per_time_slice = 1.0 * (ticks_per_beat * bpm * globals.time_slice) / 60

    # each midi file contains multiple tracks
    midi_tracks = midi_data.tracks

    max_ticks = 0
    for track in midi_tracks:
        sum_ticks = 0
        for event in track:            
            if str(event.type) == 'note_on' or str(event.type) == 'note_off' or str(event.type) == 'end_of_track':
                # add all ticks to sum
                sum_ticks += event.time

        # set maximum to highest ticks in track
        # max_ticks: 109440
        if sum_ticks > max_ticks:
            max_ticks = sum_ticks

    # 109440 / 38.5 = 2834
    # = amount of ticks we feed to network
    time_slices = int(ceil(max_ticks / ticks_per_time_slice))

    vector_dimension = 49    
    # create empty matrix with all zeros
    midi_matrix = np.zeros((vector_dimension, time_slices))

    active_notes = {}
    highest_note = 81 # A5
    loweset_note = 33 # A1


    # Loop to save active notes in midi_matrix.
    for track in midi_tracks:
        total_ticks = 0
        for event in track:
            # if note on
            if str(event.type) == 'note_on' and event.velocity > 0:
                total_ticks += event.time
                # get position of time slice on x axis, time_slice dimension
                current_time_slice_idx = int(total_ticks / ticks_per_time_slice)

                # truncate midi file to pre-defined note range
                # E.g. A3 = 57
                if event.note <= highest_note and event.note >= loweset_note:
                    note_idx = event.note - loweset_note # transform note from 57 - xx to 0 - xx
                    # write activate note event to the correct position in the matrix
                    midi_matrix[note_idx][current_time_slice_idx] = 1
                    # save time slice idx
                    # 50, 100, 150
                    active_notes[note_idx] = current_time_slice_idx
                    
            elif str(event.type) == 'note_off' or ( str(event.type) == 'note_on' and event.velocity == 0 ):
                note_idx = event.note - loweset_note
                total_ticks += event.time
                current_time_slice_idx = int(total_ticks / ticks_per_time_slice)

                if note_idx in active_notes:
                    last_time_slice_index = active_notes[note_idx]
                    # Fill the matrix with 1's on the correct position between the note on and note off event
                    midi_matrix[note_idx][last_time_slice_index:current_time_slice_idx] = 1
                    del active_notes[note_idx]


    # transpose matrix
    return midi_matrix.T

def generateNetworkInputs(midi_matrixes, x_length, y_length):
    x = []
    y = []

    for i, midi_matrix in enumerate(midi_matrixes):
        idx = 0

        # check summation of sequence lenght against length of total midi track : E.g 2834
        while idx + x_length + y_length < midi_matrix.shape[0]:
            x.append(midi_matrix[idx : idx + x_length])
            y.append(midi_matrix[idx + x_length : idx + x_length + y_length])
            idx = idx + x_length

    X = np.array(x)
    Y = np.array(y)

    x_1, y_1 = shuffle(X, Y)

    return x_1, y_1

# test generate print test length
def generateTestNetworkInputs(midi_matrixes, sequence_length):
    test = []

    for i, midi_matrix in enumerate(midi_matrixes):
        x = []
        idx = 0
        while idx + sequence_length < midi_matrix.shape[0]:
            x.append(midi_matrix[idx:idx + sequence_length])
            idx = idx + 1
        test.append(np.array(x))

    return np.array(test)

