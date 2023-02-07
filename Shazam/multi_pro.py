import Match as Mt
import os

# 给定待匹配歌曲目录，匹配后结果写入res2.txt文件中
path = ".\\testdata\\"
dist = open('res2.txt', mode='w', encoding='utf-8')
path1 = ".\\indexs.txt"
path2 = ".\\id_name.txt"
Mt.get_index(path1, path2)  # 读取特征
for i, audio1 in enumerate(os.listdir(path)):
    ts = path + audio1
    print("processing" + ts)
    dist.write(ts)
    res = Mt.work(ts)
    dist.write(res)
    dist.write('\n')
dist.close()
