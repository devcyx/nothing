"""
Description:
Author: song bo
Action      Date        Content
------------------------------------
Create      2019-
"""
import datetime
import os
from multiprocessing import Process
import time

from scrapy import cmdline

from NemsSpider.utils.login import Login, DWLogin


# input_date = [
#     {"inputDateStart": "20180101", "inputDateEnd": "20180131"}
#     , {"inputDateStart": "20180201", "inputDateEnd": "20180228"}
#     , {"inputDateStart": "20180301", "inputDateEnd": "20180331"}
#     , {"inputDateStart": "20180401", "inputDateEnd": "20180430"}
#     , {"inputDateStart": "20180501", "inputDateEnd": "20180531"}
#     , {"inputDateStart": "20180601", "inputDateEnd": "20180630"}
#     , {"inputDateStart": "20180701", "inputDateEnd": "20180731"}
#     , {"inputDateStart": "20180801", "inputDateEnd": "20180831"}
#     , {"inputDateStart": "20180901", "inputDateEnd": "20180930"}
#     , {"inputDateStart": "20181001", "inputDateEnd": "20181031"}
#     , {"inputDateStart": "20181101", "inputDateEnd": "20181130"}
#     , {"inputDateStart": "20181201", "inputDateEnd": "20181231"}
#     , {"inputDateStart": "20190101", "inputDateEnd": "20190131"}
#     , {"inputDateStart": "20190201", "inputDateEnd": "20190228"}
#     , {"inputDateStart": "20190301", "inputDateEnd": "20190331"}
#     , {"inputDateStart": "20190401", "inputDateEnd": "20190430"}
#     , {"inputDateStart": "20190501", "inputDateEnd": "20190531"}
# ]


def run():
    while 1:
        # while True:
        # time.sleep(30)
        now = datetime.datetime.now()
        now_hour = int(datetime.datetime.now().strftime("%H"))
        job_list = [run_nems_spider, run_dec_spider, run_dw_dec_spider]  # 任务列表
        if now_hour == 22 and now.weekday() == 6:
            # 每周日22:00更新上周核注清单数据
            for job in job_list:
                p = Process(target=job, args=(False, ), daemon=True)
                p.start()
        # 每天核注清单数据每小时更新一次（更新时间段：8：00-22：00）
        if 8 <= now_hour <= 22:
            for job in job_list:
                p = Process(target=job, daemon=True)
                p.start()
            time.sleep(60 * 60)
        else:
            time.sleep(60 * 60 * 10)


def run_nems_spider(is_today=True):
    now = datetime.datetime.now()
    now_hour = int(datetime.datetime.now().strftime("%H"))
    name = 'task[%d]' % os.getpid()
    print(f'核注清单--{now_hour}的任务：{name} start 跑起来')
    # if now_hour in [8, 10, 12, 14, 16, 18, 20, 22]:
    a = Login("nems")
    a.start_requests()
    # os.system(f'scrapy crawl nems -a input_date={input_date} -a is_today={is_today}')
    if is_today:
        start_date = datetime.datetime.today().strftime("%Y%m%d")
        end_date = datetime.datetime.today().strftime("%Y%m%d")
    else:
        start_date = (now - datetime.timedelta(days=now.weekday()+7)).strftime("%Y%m%d")
        end_date = (now - datetime.timedelta(days=now.weekday() + 1)).strftime("%Y%m%d")

    input_date = [{"inputDateStart": start_date, "inputDateEnd": end_date}]
    cmdline.execute(['scrapy', 'crawl', '-a', f'input_date={input_date}', '-a', f'is_today={is_today}', 'nems'])


def run_dec_spider(is_today=True):
    now = datetime.datetime.now()
    now_hour = int(datetime.datetime.now().strftime("%H"))
    name = 'task[%d]' % os.getpid()
    print(f'报关单--{now_hour}的任务：{name} start 跑起来')
    # if now_hour in [8, 10, 12, 14, 16, 18, 20, 22]:
    a = Login("dec")
    a.start_requests()
    if is_today:
        start_date = datetime.datetime.today().strftime("%Y-%m-%d")
        end_date = datetime.datetime.today().strftime("%Y-%m-%d")
    else:
        start_date = (now - datetime.timedelta(days=now.weekday()+7)).strftime("%Y-%m-%d")
        end_date = (now - datetime.timedelta(days=now.weekday() + 1)).strftime("%Y-%m-%d")
    input_date = [{"updateTime": start_date, "updateTimeEnd": end_date}]
    # os.system(f'scrapy crawl nems -a input_date={input_date} -a is_today={is_today}')
    cmdline.execute(['scrapy', 'crawl', '-a', f'input_date={input_date}', '-a', f'is_today={is_today}', 'dec'])


def run_dw_dec_spider(is_today=True):
    now = datetime.datetime.now()
    now_hour = int(datetime.datetime.now().strftime("%H"))
    name = 'task[%d]' % os.getpid()
    print(f'东莞报关单--{now_hour}的任务：{name} start 跑起来')
    # if now_hour in [8, 10, 12, 14, 16, 18, 20, 22]:
    a = DWLogin()
    a.start_requests()
    if is_today:
        start_date = datetime.datetime.today().strftime("%Y-%m-%d")
        end_date = datetime.datetime.today().strftime("%Y-%m-%d")
    else:
        start_date = (now - datetime.timedelta(days=now.weekday()+7)).strftime("%Y-%m-%d")
        end_date = (now - datetime.timedelta(days=now.weekday() + 1)).strftime("%Y-%m-%d")
    input_date = [{"updateTime": start_date, "updateTimeEnd": end_date}]
    # os.system(f'scrapy crawl nems -a input_date={input_date} -a is_today={is_today}')
    cmdline.execute(['scrapy', 'crawl', '-a', f'input_date={input_date}', '-a', f'is_today={is_today}', 'dw_dec'])


if __name__ == '__main__':
    run()
