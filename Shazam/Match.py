import librosa as lb
import numpy as np
from scipy import ndimage
import matplotlib.pyplot as plt
import os
from pydub import AudioSegment


# 读取歌曲文件并获取时频矩阵（幅值）
def compute_spectrogram(audio_path, Fs=22050, N=2048, H=1024, bin_max=256, frame_max=None):
    # FS是采样率，bin_max是纵轴限制(频率)，frame_max是横轴（时间）
    # Librosa默认的采样率是22050，如果需要读取原始采样率，需要设定参数sr = None:
    x, Fs = lb.load(audio_path)
    X = lb.stft(x, n_fft=N, hop_length=H, win_length=N, window='hanning')
    if bin_max is None:
        bin_max = X.shape[0]
    if frame_max is None:
        frame_max = X.shape[1]
    Y = np.abs(X[:bin_max, :frame_max])
    # Y = np.abs(X)
    return Y


# 计算constellation map，并返回带有peak位置的01矩阵
def compute_constellation_map(Y, dist_freq=7, dist_time=7, thresh=0.01, ptype=0):
    # Y是时频图，dist_freq和dist_time邻域大小参数，前者是频率方向上，后者是时间方向上，thresh是peak强度阈值
    # 计算后返回一个01矩阵Cmap
    result = ndimage.maximum_filter(Y, size=[2 * dist_freq + 1, 2 * dist_time + 1], mode='constant')
    Cmap = np.logical_and(Y == result, result > thresh)
    if ptype == 0:
        return Cmap  # 不做变速匹配
    else:
        return np.delete(Cmap, np.where(~Cmap.any(axis=0))[0], axis=1)  # 删除0列，即空白帧


to_point = {}  # 索引表建立表工具


# 划分zone计算特征
def compute_zone(cmap, dist=5, m_id=1, gap=5):
    # 锚点和zone的距离为gap
    # 由Ft_point 右移16位得到锚点时间，再用Ft_point减掉右移后的数得到曲目id
    # 返回一个正整数序列
    # cmap即计算的constellation_map,dist即zone的区域大小,m_id即对应歌曲id
    pos = np.argwhere(cmap.T == 1)  # 记录下所有为1的坐标
    # print(pos)
    for i in range(len(pos) - dist + 1 - gap):
        for j in range(dist):
            # pos[i]为锚点，用pos[i+j]与pos[i]计算一个64位无符号整数，形成该曲目的一个特征点
            x, y = pos[i]  # x时间，y频率
            xt, yt = pos[i + j + gap]
            a = y
            b = yt
            c = abs(xt - x)
            # [a, b, c] : 锚点频率、当前点频率、时间差
            # [a, b, c] => [x, id] a,b各占9位，c占14位，id占16位,锚点时间占16位，总共可以形成两个32位无符号整数
            Sum = (a << 23) + (b << 14) + c
            Ft_point = (x << 16) + m_id
            # Sum => Ft_point
            if Sum in to_point:
                pass
            else:
                to_point[Sum] = []
            to_point[Sum].append(Ft_point)


def compute_all(path, dist_freq=11, dist_time=7, zone_dist=5, gap=5, bin_max=256, ptype=0):  # 计算音乐库的索引
    # ind_dir是要建立索引的音乐库
    id_name = open('id_name.txt', mode='w', encoding='utf-8')
    idx = 1
    for fn in os.listdir(path):
        tfn = os.path.join(path, fn)
        if os.path.isfile(tfn):
            if fn.endswith(".wav"):
                # to_name.append(fn)      # 音乐id从0增长
                id_name.write(str(idx) + ' ' + fn + '\n')
                Y = compute_spectrogram(tfn, bin_max=bin_max)
                cmap = compute_constellation_map(Y, dist_freq=dist_freq, dist_time=dist_time, ptype=ptype)
                # para2 = np.log(1 + 1 * Y)
                # fig, ax, img = plot_constellation_map(cmap, para2, color='r', s=30)
                compute_zone(cmap, dist=zone_dist, m_id=idx, gap=gap)
                print('processing:' + str(idx))
                idx = idx + 1
    index = open('indexs.txt', mode='w', encoding='utf-8')
    for keys in to_point:
        index.write(str(keys))
        for tx in to_point[keys]:
            index.write(' ' + str(tx))
        index.write('\n')
    id_name.close()
    index.close()


id_index = dict()
ft_index = dict()


def get_index(index_path, id_path):
    # 从index_path文件中读取出特征索引，并将索引以{num:[num...]}的形式返回
    # 从id_path文件中读出歌曲名和对应的id并返回{id:歌曲名}
    fn1 = open(index_path, 'r', encoding='utf-8')
    fn2 = open(id_path, 'r', encoding='utf-8')
    for line in fn2.readlines():
        line = line.strip()
        i = 0
        while line[i] != ' ':
            i += 1
        idx = int(line[:i])
        id_index[idx] = line[i:].strip()
    for line in fn1.readlines():
        tp = line.split()
        tplist = []
        for i in range(1, len(tp)):
            tplist.append(int(tp[i]))
        ft_index[int(tp[0])] = tplist
    fn1.close()
    fn2.close()


def compare_song(path, dist_freq=11, dist_time=7, zone_dist=5, gap=5, thresh=1, song_range=10, bin_max=256, ptype=0):
    # 给定歌曲路径，在特征库中检索并给出结果
    y = compute_spectrogram(path, bin_max=bin_max)
    cmap = compute_constellation_map(y, dist_freq, dist_time, ptype=ptype)
    pos = np.argwhere(cmap.T == 1)  # 记录下所有为1的坐标
    res = dict()
    # allpoint = (len(pos) - zone_dist + 1) * zone_dist  # 总特征点数
    for i in range(len(pos) - zone_dist + 1 - gap):
        for j in range(zone_dist):
            # pos[i]为锚点，用pos[i+j+gap]与pos[i]计算一个64位无符号整数，形成该曲目的一个特征点
            x, y = pos[i]  # x时间，y频率
            xt, yt = pos[i + j + gap]
            a = y
            b = yt
            c = abs(xt - x)
            # [a, b, c] : 锚点频率、当前点频率、时间差
            # [a, b, c] => [x, id] a,b各占9位，c占14位，id占16位,锚点时间占16位，总共可以形成两个32位无符号整数
            Sum = (a << 23) + (b << 14) + c
            # 用Sum在特征库中检索
            if Sum in ft_index:
                for lx in ft_index[Sum]:
                    if lx in res:
                        res[lx] += 1
                    else:
                        res.setdefault(lx, 1)
    for keys in list(res):
        if res[keys] <= thresh:
            res.pop(keys)
    ans = sorted(zip(res.values(), res.keys()))  # 最终返回了一个以计数次数升序的元组列表，元组第一元素为出现次数，第二元素为歌曲id和锚点时间
    ans.reverse()
    Len = len(ans)
    if Len == 0:
        # print("没有检测到相似歌曲")
        return "没有检测到相似歌曲"
    if Len < song_range:
        song_range = Len

    # 输出匹配度最高的前song_range首曲目
    test = dict()
    for tp in ans:
        feq = tp[0]  # 出现频次
        anchor_time = tp[1] >> 16
        idx = tp[1] - (anchor_time << 16)
        if idx in test:
            test[idx] += feq
        else:
            test.setdefault(idx, feq)
    tst = sorted(zip(test.values(), test.keys()))
    tst.reverse()
    cnt = 1
    putres = "匹配到以下歌曲最相似：\n"
    # print("匹配到以下歌曲最相似：")
    for key in tst:
        if song_range == 0:
            break
        song_range -= 1
        # print("第" + str(cnt) + "名： " + id_index[key[1]] + "： " + str(key[0]))
        putres = putres + "第" + str(cnt) + "名： " + id_index[key[1]] + "： " + str(key[0]) + "\n"
        cnt += 1
    return putres


def mp3_to_wav(src):
    # 输入mp3文件并转换成对应wav格式的文件（置于特定目录下）
    dst = ".\\music\\Final\\testdata\\temp.wav"
    # dst = src.split('.mp3')[0] + '.wav'
    sound = AudioSegment.from_mp3(src)
    sound.export(dst, format="wav")
    return dst


def work(path):
    # path为待匹配曲目路径
    # path1 = ".\\indexs.txt"
    # path2 = ".\\id_name.txt"
    # path1 = ".\\FingerPrint\\pop\\indexs.txt"
    # path2 = ".\\FingerPrint\\pop\\id_name.txt"
    # get_index(path1, path2)  # 读取特征
    # 开始检索
    cmp = path
    # 如果是mp3文件先转成wav
    t1 = cmp.find('.mp3')
    t2 = cmp.find('.wav')
    if t1 != -1:
        cmp = mp3_to_wav(path)
    elif t2 != -1:
        cmp = path
    else:
        # print("无法处理的音频格式！")
        return "无法处理的音频格式！"

    # res = compare_song(path=cmp, dist_freq=11, dist_time=7, thresh=1, zone_dist=7, gap=7, bin_max=512, ptype=1)  # 变速
    # res = compare_song(path=cmp, dist_freq=11, dist_time=7, thresh=1, zone_dist=5, gap=7, bin_max=256, ptype=1)  # lx变速
    # res = compare_song(path=cmp, dist_freq=9, dist_time=5, thresh=13, zone_dist=11, gap=5, bin_max=256, ptype=0)
    # res = compare_song(path=cmp, dist_freq=11, dist_time=7, thresh=5, zone_dist=7, gap=7, bin_max=256, ptype=0)
    # res = compare_song(path=cmp, dist_freq=11, dist_time=7, thresh=1, zone_dist=5, gap=5, bin_max=256, ptype=0)  # 流行音乐匹配
    res = compare_song(path=cmp, dist_freq=11, dist_time=7, thresh=1, zone_dist=5, gap=5, bin_max=256, ptype=0)
    return res

# 生成所有音乐的索引
# if __name__ == '__main__':
#     compute_all(".\\music\\Final\\database", 9, 5, 11, 5, 256, 0)
# plt.show()
