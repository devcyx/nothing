# -*- coding: utf-8 -*-
import copy
import datetime
import hashlib
import json
import re

import requests
import scrapy

from NemsSpider.items import NemsspiderItem
from NemsSpider.utils.redis_app import RedisApp
pyredis = RedisApp().get_redis_instance()

from NemsSpider.utils.log import getlogger

log = getlogger(__name__)


class NemsSpider(scrapy.Spider):
    name = 'nems'
    allowed_domains = ['singlewindow.cn']
    start_urls = r'http://sz.singlewindow.cn/dyck/swProxy/sasserver/sw/ems/invt/Bws/list'
    detial_post_url = r'http://sz.singlewindow.cn/dyck/swProxy/sasserver/sw/ems/invt/Bws/details/{}'

    def __init__(self, input_date=None, is_today='True', *args, **kwargs):
        super(NemsSpider, self).__init__(*args, **kwargs)
        self.input_date = eval(input_date)
        self.is_today = eval(is_today)  # 判断是否更新当日数据

    def start_requests(self):
        def get_post_data():
            for one_time in self.input_date:
                postdata1 = copy.deepcopy(postdata)
                postdata1.update(one_time)
                for one_ie in ie_data:
                    postdata2 = copy.deepcopy(postdata1)
                    postdata2.update(one_ie)
                    for one_start in start_data:
                        postdata3 = copy.deepcopy(postdata2)
                        postdata3.update(one_start)
                        yield postdata3
        cookies = json.loads(pyredis.get("request_cookies"))
        postdata = {"selTradeCode": "4403W60001", "bondInvtNo": "", "seqNo": "", "bizopEtpsNo": ""}
        ie_data = [{"impExpMarkCd": "I", "impExpMarkCdName": "进口"}, {"impExpMarkCd": "E", "impExpMarkCdName": "出口"}]
        start_data = [{"status": "B", "statusName": "海关终审通过"}, {"status": "P", "statusName": "预审批通过"}]
        headers = {
            "Content-Type": "application/json",
            "User-Agent": 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
        }

        for data in get_post_data():
            yield scrapy.Request(url=self.start_urls, method="POST", meta={"data":data}, callback=self.parse, cookies=cookies,
                                 headers=headers, body=json.dumps(data), dont_filter=True)

    def parse(self, response):
        # 返回json数据
        data = response.meta.get("data")
        rs = json.loads(response.text)
        if rs.get("code") == 1:
            log.warning(f'{rs.get("message")}, 请求数据：{data}')
        elif rs.get("code") == 0:
            now = datetime.datetime.now()
            first_week_day = (now - datetime.timedelta(days=now.weekday())).strftime("%Y%m%d")  # 本周第一天
            for item in rs.get("data").get("resultList"):
                is_update = False  # 判断是否更新
                if self.is_today:
                    # 只更新当日数据
                    ret = pyredis.hsetnx(f'nems{first_week_day}', item.get("seqNo"), item.get("listStat"))  # 插入本周的数据集
                else:
                    # 更新上周数据 插入上周的数据集
                    ret = pyredis.hsetnx(f'nems{data.get("inputDateStart")}', item.get("seqNo"), item.get("listStat"))

                if ret == 0 and pyredis.hget(f'nems{data.get("inputDateStart")}', item.get("seqNo")) == item.get("listStat"):
                    # 如果seqNo已存在 redis 且数据状态一致（可能都是终审判通过）则不更新数据
                    continue
                elif ret == 0:
                    # 如果seqNo已存在 redis 且数据状态不一致则更新数据  ## 其他则新增数据
                    pyredis.hset(f'nems{first_week_day}', item.get("seqNo"), item.get("listStat"))  # 更新redis 数据状态
                    is_update = True
                # 创建item
                msg = {
                    'ClientSeqNo': ""
                    , 'DecState': "CR_4" if item.get("listStat") == "P" else "CR_9"
                    , 'QpSeqNo': item.get("seqNo")
                    , 'QpEntryId': item.get("bondInvtNo")
                    , 'QpNotes': ""
                    , 'EdocFiles': ""
                    , 'CreateTime': item.get("invtDclTime")
                    , 'CreateUser': "spider"
                    , 'ProcessTime': item.get("invtDclTime")
                    , 'ProcessUser': ""
                    , 'MoreCategory': 98
                    , 'DeleteFlag': 0
                    , 'IsContrast': "未对比"
                    , 'IsNotify': 0
                    , 'LicenseState': 0
                    , 'SyncState': 0
                    , 'BtOperationNum': ""
                }
                yield scrapy.Request(url=self.detial_post_url.format(item.get("seqNo")), method="POST",
                                     meta={"data": msg, "is_update": is_update, "first_week_day": first_week_day},
                                     callback=self.parse_item, dont_filter=True)
        else:
            log.error(f"有问题！！{response.request.url}")

    def parse_item(self, response):
        # 创建item
        item = NemsspiderItem()
        item["msg"] = response.meta.get("data")
        item["is_update"] = response.meta.get("is_update")
        item["first_week_day"] = response.meta.get("first_week_day")
        # 解析返回json数据
        try:
            rs = json.loads(response.text)
            item["headers"] = rs.get("data").get("invtHeadType")
            item["lists"] = rs.get("data").get("invtListType")
            item["msg"]["CreateTime"] = rs.get("data").get("invtHeadType").get("inputTime")
            yield item
        except Exception as e:
            retry = response.request.copy()
            retry_times = retry.meta.get('retry_times', 0)
            if retry_times == 4:
                log.error(f'url: {response.request.url} 重试了4次还有问题：{response.text}， 错误{traceback.format_exc()}')
            retry.dont_filter = True  #这个一定要有，否则重试的URL会被过滤
            retry.meta['retry_times'] = retry_times +1
            yield retry


