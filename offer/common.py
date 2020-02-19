# 时间装饰器
import time
from functools import wraps

def cal_time(func):
    @wraps(func)
    def run_func(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        end_time = time.time()
        print(f'{func.__name__} 的运行时间:{end_time-start_time}')
    return wrapper
