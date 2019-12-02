from kivy.app import App
from kivy.core.window import Window
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button

from mido import play_midi

import model
import predict_song

class BeathovenGridLayout(GridLayout):
    folder_path = ''

    def play_midi(self):
        play_midi.play_music('C:\dev\school\minor_ai\minor_ai_repo\Beathoven2.4\generatedLSTM_gen_20190606_12_49.mid')

    def train(self):
        model.train(self.folder_path)

    def generate_song(self):
        predict_song.run(self.folder_path)

class BeathovenApp(App):
    Layout = BeathovenGridLayout

    def build(self):
        Window.bind(on_dropfile=self._on_file_drop)
        return self.Layout()

    def _on_file_drop(self, window, file_path):
        self.Layout.folder_path = file_path
        print(self.Layout.folder_path)

if __name__ == '__main__':
    BeathovenApp().run()