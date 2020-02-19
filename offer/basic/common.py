# 时间装饰器
import time
from functools import wraps

def cal_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        end_time = time.time()
        print(f'{func.__name__} 的运行时间:{end_time-start_time}')
    return wrapper

import multiprocessing

def p1(x):
    print(x)

if __name__ == '__main__':
    a = []
    for i in range(10):
        targe = multiprocessing.Process(target=p1, args=(i,))
        targe.start()
        a.append(targe)
    # for i in a:
    #     i.start()
