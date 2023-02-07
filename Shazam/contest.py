def proc(root, bd):
    if root > bd:
        return
    proc(root * 2, bd)
    proc(root * 2 + 1, bd)
    if root * 2 <= bd:
        if rt[root * 2] == 'B' and rt[root * 2 + 1] == 'B':
            rt[root] = 'B'
        elif rt[root * 2] == 'I' and rt[root * 2 + 1] == 'I':
            rt[root] = 'I'
        else:
            rt[root] = 'F'
    print(rt[root], end='')


n = int(input())
s = input()
rt = ['0'] * (2 ** (n + 1))
d = len(rt)
j = len(s)-1
for i in range(d - 1, d - len(s) - 1, -1):
    if s[j] == '0':
        rt[i] = 'B'
    else:
        rt[i] = 'I'
    j = j-1
proc(1, d - 1)
