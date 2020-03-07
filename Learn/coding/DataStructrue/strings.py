"""
Description: 字符串
Author: Alvin yx
Action      Date        Content
------------------------------------
Create      2019-11-05  Add
"""


# 朴素的串匹配法
def naive_matching(t, p):
    p_len, t_len = len(p), len(t)
    i, j = 0, 0
    while i < p_len and j < t_len:
        if p[i] == t[j]:
            i, j = i+1, j+1
        else:
            i, j = 0, j-i+1
    if i == p_len:
        return j - i
    else:
        return -1


if __name__ == '__main__':
    print(naive_matching("0001", "01"))


