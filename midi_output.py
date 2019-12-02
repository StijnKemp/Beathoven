import numpy as np
import mido as m
import globals

# time_slice: [3.29636059e-05 2.10659255e-05 3.77731412e-05 5.27929187e-05
#  			   6.77127609e-05 4.24078862e-05 3.58403631e-05 5.11402577e-05
#  			   2.92296299e-05 2.07472804e-05 2.78930765e-05 3.52825882e-05
#  			   4.12259287e-05 4.06611252e-05 4.12585759e-05 2.61970254e-05
#  			   1.43563928e-04 1.10810615e-04 7.75936860e-05 1.56892056e-04
#  			   2.16739609e-05 5.22122136e-05 5.40118381e-05 9.01570675e-05
#  			   8.61312583e-05 4.30314903e-05 7.83486466e-05 2.97490682e-04
#  			   5.31654165e-04 6.78948185e-04 2.36720056e-03 2.14526826e-03
#  			   2.73393630e-03 1.06888162e-02 3.69552881e-01 2.19572354e-02
#  			   2.69522704e-02 5.03928773e-02 9.09177139e-02 4.74110357e-02
#  			   4.67460863e-02 1.25592500e-01 6.19718693e-02 9.29303095e-02
#  			   1.92897972e-02 1.18849855e-02 1.22684147e-02 3.41207167e-04
#  			   8.28867371e-04] -> count 49
# idx: [34, 41]
# net_roll: (141250, 49)

# determine which notes are going to be on per time slice depending on the threshold
def networkOutToMatrix(output, threshold = 0.1):
    midi_matrix = []
    for sequence in output:
            for time_slice in sequence:
                idx = [i for i, t in enumerate(time_slice) if t > threshold]
                midi_matrix_slice = np.zeros(time_slice.shape)
                midi_matrix_slice[idx] = 1
                midi_matrix.append(midi_matrix_slice)

    return np.array(midi_matrix)
# output
# [[0. 0. 0. ... 0. 0. 0.]
#  [0. 0. 0. ... 0. 0. 0.]
#  [0. 0. 0. ... 0. 0. 0.]
#  ...
#  [0. 0. 0. ... 0. 0. 0.]
#  [0. 0. 0. ... 0. 0. 0.]
#  [0. 0. 0. ... 0. 0. 0.]]

def matrixToMidi(midi_matrix, path):
    ticks_per_time_slice = 1
    # 1 / 0.20 = 50
    time_per_time_slice = 0.02 # do this in config
    bpm = 1 / time_per_time_slice
    ticks_per_beat = 60 * ticks_per_time_slice / (bpm * time_per_time_slice)

    midiFile = m.MidiFile(ticks_per_beat = int(ticks_per_beat))
    track = m.MidiTrack()
    midiFile.tracks.append(track)
    track.append(m.MetaMessage('set_tempo', tempo = int(globals.microseconds_per_minute / bpm), time = 0))

    vector_dimension = 49
    current_state = np.zeros(vector_dimension)

    last_event_index = 0
    # highest_note = 81 # A5
    # loweset_note = 33 # A1


    for slice_index, time_slice in enumerate(np.concatenate((midi_matrix, np.zeros((1, vector_dimension))), axis = 0)):
        # can change 1 to 0, and 0 to -1. 
        note_changes = time_slice - current_state

        # compare previous time slice for note on OR note off event. Only make note on event when a time_slice starts a note
        for note_idx, note in enumerate(note_changes):
            if note == 1:
                note_event = m.Message('note_on', time = (slice_index - last_event_index) * ticks_per_time_slice, velocity = 65, note = note_idx + globals.lowest_note)
                track.append(note_event)
                last_event_index = slice_index
            elif note == -1:
                note_event = m.Message('note_off', time = (slice_index - last_event_index) * ticks_per_time_slice, velocity = 65, note = note_idx + globals.lowest_note)
                track.append(note_event)
                last_event_index = slice_index
        
        current_state = time_slice

    track.append(m.MetaMessage('end_of_track', time = 1))

    midiFile.save(path)