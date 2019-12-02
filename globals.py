import os
from keras.optimizers import Adam

base_path = os.path.dirname(os.path.abspath(__file__))

weights_directory = os.path.join(base_path, "", "weights")
model_directory = os.path.join(base_path, "", "models")
midi_directory = os.path.join(base_path, "", "midi")
generated_midi_directory = os.path.join(base_path, "", "models")


time_slice = 0.02
highest_note = 81
lowest_note = 33
input_dimension = highest_note - lowest_note + 1
output_dimension = highest_note - lowest_note + 1
microseconds_per_minute = 60000000

# model stuff
loss_function = 'categorical_crossentropy'
optimizer = Adam()

x_sequence_length = 50 # sliding window
y_sequence_length = 50 