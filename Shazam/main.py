import pyaudio
import threading
import wave
import tkinter
import Match as Mt
from tkinter import filedialog


class Recorder:
    def __init__(self, chunk=1024, channels=2, rate=44100):
        self.CHUNK = chunk
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = channels
        self.RATE = rate
        self._running = True
        self._frames = []

    def start(self):
        threading._start_new_thread(self.__recording, ())

    def __recording(self):
        self._running = True
        lbl['text'] = '开始录音'
        lbl2['text'] = ''
        lblres['text'] = ''
        self._frames = []
        p = pyaudio.PyAudio()
        stream = p.open(format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.RATE,
                        input=True,
                        frames_per_buffer=self.CHUNK)
        while self._running:
            data = stream.read(self.CHUNK)
            self._frames.append(data)

        stream.stop_stream()
        stream.close()
        p.terminate()

    def stop(self):
        self._running = False
        lbl['text'] = '停止录音'

    def openf(self):
        lbl['text'] = '匹配中'
        lblres['text'] = ''
        sel_path = filedialog.askopenfilename()
        t = sel_path.find('.wav')
        if t == -1:
            t = sel_path.find('.mp3')
            if t == -1:
                lbl['text'] = '非法文件格式'
                return
        lbl2['text'] = '当前歌曲目录：' + sel_path
        lbl['text'] = '匹配完成'
        res = Mt.work(sel_path)
        lblres['text'] = res

    def save(self):
        # 保存录音并调用检索
        lbl['text'] = '匹配中'
        p = pyaudio.PyAudio()
        wf = wave.open(".\\music\\Final\\testdata\\temp.wav", 'wb')
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b''.join(self._frames))
        wf.close()
        res = Mt.work('.\\music\\Final\\testdata\\temp.wav')
        # 输出返回结果
        lbl['text'] = '匹配完成'
        lblres['text'] = res


if __name__ == '__main__':
    # 创建窗口
    window = tkinter.Tk()
    # 给窗口命名
    window.title("音乐匹配")
    # 设置窗口大小
    window.geometry("1000x700")
    re = Recorder()
    # 根据索引文件加载数据
    path1 = ".\\FingerPrint\\indexs.txt"
    path2 = ".\\FingerPrint\\id_name.txt"
    # path1 = ".\\indexs.txt"
    # path2 = ".\\id_name.txt"
    # path1 = ".\\FingerPrint\\piano\\正常处理\\indexs.txt"
    # path2 = ".\\FingerPrint\\piano\\正常处理\\id_name.txt"
    Mt.get_index(path1, path2)  # 读取特征

    # 设置一个录音按钮
    b1 = tkinter.Button(window, text="开始录音", font=("FangSong", 14), width=10, height=1, command=re.start)
    b1.place(x=10, y=10, anchor="nw")
    # 设置一个停止按钮
    b2 = tkinter.Button(window, text="结束录音", font=("FangSong", 14), width=10, height=1, command=re.stop)
    b2.place(x=130, y=10, anchor="nw")
    # 设置一个保存按钮
    b3 = tkinter.Button(window, text="开始匹配", font=("FangSong", 14), width=10, height=1, command=re.save)
    b3.place(x=250, y=10, anchor="nw")
    # 设置一个文件打开按钮
    bf = tkinter.Button(window, text="文件中匹配", font=("FangSong", 14), width=10, height=1, command=re.openf)
    bf.place(x=370, y=10, anchor="nw")
    lbl = tkinter.Label(window, text="欢迎使用", font=("FangSong", 14))
    lbl.place(x=10, y=50, anchor="nw")
    lbl2 = tkinter.Label(window, text="...", font=("FangSong", 14))
    lbl2.place(x=10, y=75, anchor="nw")
    lblres = tkinter.Label(window, text="", font=("FangSong", 14))
    lblres.place(x=10, y=100, anchor="nw")
    # 主窗口循环
    window.mainloop()
