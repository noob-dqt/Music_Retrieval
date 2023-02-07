from os import path
from pydub import AudioSegment
import os


# MP3格式歌曲批量转换为wav文件

def trans_to_wav(mp3_file, wav_folder):
    # convert wav to mp3
    dst = os.path.join(wav_folder)
    dst = os.path.join(dst, '{}.{}'.format(os.path.basename(mp3_file).strip().split('.')[0], 'wav'))
    print(dst)
    sound = AudioSegment.from_mp3(mp3_file)
    sound.export(dst, format="wav")


def read_folder(mp3_folder, wav_folder):
    # 遍历需要转换的MP3文件夹中的MP3文件
    for a in os.listdir(mp3_folder):
        # 创建MP3文件的绝对路径
        mp3_file = os.path.join(mp3_folder, a)
        # 调用格式转换函数
        trans_to_wav(mp3_file, wav_folder)


if __name__ == '__main__':
    mp3_folder = '.\\music\\Final\\test'
    wav_folder = ".\\music\\Final\\database"
    read_folder(mp3_folder, wav_folder)
