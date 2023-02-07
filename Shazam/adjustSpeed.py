import os
import sys
from ffmpeg import audio

audio_path = ".\\music\\big\\faster\\tp\\"
finish_path = ".\\music\\big\\faster\\"


def run():
    audio_file = os.listdir(audio_path)
    for i, audio1 in enumerate(audio_file):
        # print(audio_path + audio1)
        ts = audio_path + audio1
        ts = ts.replace(' ', '_')
        print(ts)
        # audio.a_speed(ts, "2", finish_path + audio1)


run()
