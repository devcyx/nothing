"""
Description:
Author: song bo
Action      Date        Content
------------------------------------
Create      2019-
"""
import datetime
import os
from scrapy import cmdline

from NemsSpider.utils.login import Login


def run_nems_spider():
    now = datetime.datetime.now()
    now_hour = int(datetime.datetime.now().strftime("%H"))
    name = 'task[%d]' % os.getpid()
    print(f'核注清单--{now_hour}的任务：{name} start 跑起来')
    a = Login("nems")
    a.start_requests()
    start_date = (now - datetime.timedelta(days=3)).strftime("%Y%m%d")
    end_date = (now - datetime.timedelta(days=1)).strftime("%Y%m%d")

    input_date = [{"inputDateStart": start_date, "inputDateEnd": end_date}]
    cmdline.execute(['scrapy', 'crawl', '-a', f'input_date={input_date}', '-a', f'is_today=False', 'nems'])


if __name__ == '__main__':
    run_nems_spider()
