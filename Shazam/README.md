### 记录实现Shazam公司提供的音乐检索经典方法
main.py为入口文件，需要先生成id_name.txt 和 index.txt两个必备索引库，生成代码位于Match.py中
##### 该方法用于流行音乐检索效果好，用于钢琴曲检索效果较差

流行音乐调试参数：res = compare_song(path=cmp, dist_freq=11, dist_time=7, thresh=1, zone_dist=5, gap=5, bin_max=256, ptype=0)