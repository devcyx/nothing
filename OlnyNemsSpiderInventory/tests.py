"""
Description:
Author: song bo
Action      Date        Content
------------------------------------
Create      2019-
"""
import os
import re
import threading
import time
from multiprocessing import Process

import requests
import scrapy
from aip import AipOcr
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

from NemsSpider import settings


class NemsSpider(object):

    login_url = "http://app.singlewindow.cn/cas/login"
    image_url = "http://app.singlewindow.cn/cas/plat_cas_verifycode_gen"
    ImageDir = './'
    aipOcr = AipOcr(settings.APP_ID, settings.API_KEY, settings.SECRET_KEY)

    def know_Image(self):
        code_count = 0
        # while code_count < 10:
        code_count += 1
        content = requests.get(self.image_url)
        with open('./images.jpg', 'wb') as f:
            f.write(content.content)
        value = self.aipOcr.basicGeneral(content.content)
        try:
            value = re.sub(r'[^a-zA-Z0-9]', '', value['words_result'][0]['words'])
        except:
            # continue
            print(value)
        if 4 == len(value) and re.match('^[0-9a-zA-Z]{4}$', value):
            return value
        else:
            print(value)


def a(i):
    name = 'task[%d]' % os.getpid()
    print('%s start' % name)
    time.sleep(1)
    print(i)
    print('%s end' % name)


if __name__ == '__main__':
    for i in range(10):
        t = Process(target=a, args=(i,), daemon=True)
        t.start()
    print("主进程----end")
