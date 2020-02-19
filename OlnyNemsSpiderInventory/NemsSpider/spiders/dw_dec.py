# -*- coding: utf-8 -*-
import copy
import datetime
import json
import time
import scrapy
import traceback

from NemsSpider.items import DecspiderItem, DWDecspiderItem
from NemsSpider.utils.log import getlogger
from NemsSpider.utils.redis_app import RedisApp
from urllib.parse import quote

log = getlogger(__name__)
pyredis = RedisApp().get_redis_instance()


class DWDecSpider(scrapy.Spider):
    name = 'dw_dec'
    allowed_domains = ['sz.singlewindow.gd.cn']
    start_urls = r'https://www.singlewindow.gd.cn/swProxy/decserver/sw/dec/merge/cusQuery?{}'
    edit_url = r"http://www.singlewindow.gd.cn/swProxy/decserver/sw/dec/merge/queryDecData"  # POST

    def __init__(self, input_date=None, is_today='True', *args, **kwargs):
        super(DWDecSpider, self).__init__(*args, **kwargs)
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
        cookies = json.loads(pyredis.get("dw_request_cookies"))
        postdata = {
            "cusCiqNoHidden": "",
            "dclTrnRelFlagHidden": "",
            "transPreNoHidden": "",
            "cusOrgCode": "",
            "operType": "0",  # 报关单查询
            "dclTrnRelFlag": "0",
            "etpsCategory": "A",
            "cusTradeNationCode": "",
            "cusTradeNationCodeName": "",
            "orgCode": "",
            "orgCodeName": "",
            "cusCiqNo": "",
            "entryId": "",
            "queryPage": "cusAdvancedQuery"  # 高级查询
        }
        ie_data = [{"cusDecStatus": ""}, {"cusDecStatus": "10"}]  # 报关状态 空是非结关 10是结关
        start_data = [{"cusIEFlag": "I"}, {"cusIEFlag": "E"}]  # I进口 E出口
        headers = {
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
            "Content-Type": "application/json"
        }

        for data in get_post_data():
            params = f'limit=10000&offset=0&stName=updateTime&stOrder=desc&decStatusInfo={quote(quote(quote(str(data))))}&_={str(time.time()).replace(".", "")[:13]}'
            yield scrapy.Request(url=self.start_urls.format(params), meta={"data": data}, callback=self.parse,
                                 headers=headers, cookies=cookies, dont_filter=True)

    def parse(self, response):
        data = json.loads(response.text)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36",
            "Content-Type": "application/json; charset=UTF-8"
        }
        now_count = len(data.get("rows"))
        now = datetime.datetime.now()
        first_post_data = response.meta.get("data")
        first_week_day = (now - datetime.timedelta(days=now.weekday())).strftime("%Y-%m-%d")  # 本周第一天
        if data.get("total") != now_count:
            log.warning(f"dw-{first_post_data.get('updateTime')}-{first_post_data.get('updateTimeEnd')}:应该获取的总数：{data.get('total')}条 实际获取的总数：{now_count}条")
        for item in data.get("rows"):
            if item.get("entryId") and item.get("cusDecStatus") in ['7', '9', '10', '11']:  # 获取所有有报关单海关编号的报关单数据（报关状态为“删除”的不用获取）

                # 存入redis
                is_update = False  # 判断是否更新
                if self.is_today:
                    # 只更新当日数据
                    ret = pyredis.hsetnx(f"dec{first_week_day}", item.get("entryId"), item.get("cusDecStatus"))  # 插入本周的数据集
                else:
                    # 更新上周数据 插入上周的数据集
                    first_week_day = first_post_data.get("updateTime")
                    ret = pyredis.hsetnx(f'dec{first_post_data.get("updateTime")}', item.get("entryId"), item.get("cusDecStatus"))

                if ret == 0 and pyredis.hget(f'dec{first_post_data.get("updateTime")}', item.get("entryId")) == item.get("cusDecStatus"):
                    # 如果seqNo已存在 redis 且数据状态一致（可能都是终审判通过）则不更新数据
                    continue
                elif ret == 0:
                    # 如果seqNo已存在 redis 且数据状态不一致则更新数据  ## 其他则新增数据
                    pyredis.hset(f"dec{first_week_day}", item.get("entryId"), item.get("cusDecStatus"))  # 更新redis 数据状态
                    is_update = True
                dec_state = {
                    "7": "CR_G",
                    "9": "CR_P",
                    "10": "CR_R",
                    "11": "CR_C"
                }

                msg = {
                    "ClientSeqNo": ""
                    , "DecState": dec_state.get(item.get("cusDecStatus"))
                    , "QpSeqNo": item.get("cusCiqNo")
                    , "QpEntryId": item.get("entryId")
                    , "QpNotes": ""
                    , "EdocFiles": ""
                    , "BlcFlag": 1
                    , "BlcState": ""
                    , "BlcNotes": ""
                    , "BlcFormId": ""
                    , 'CreateTime': datetime.datetime.strptime(item.get("indbTime"), "%Y-%m-%d %H:%M:%S")
                    , "CreateUser": "spider"
                    , "ProcessTime": datetime.datetime.strptime(item.get("updateTime"), "%Y-%m-%d %H:%M:%S")
                    , "ProcessUser": "spider"
                    , "DeleteFlag": 0
                    , "IsContrast": ""
                    , "IsNotify": 0
                    , "LicenseState": 0
                    , "SyncState": 0
                    , "BtOperationNum": ""
                    , "MoreCategory": "99"
                }
                # {"cusCiqNo":"I20190000254959881","cusIEFlag":"I","operationType":"cusEdit"}
                postdata = {"cusCiqNo": item.get("cusCiqNo"), "cusIEFlag": item.get("cusIEFlag"), "operationType": "cusEdit"}
                yield scrapy.Request(url=self.edit_url, method="POST", body=json.dumps(postdata), headers=headers,
                                     meta={"data": msg, "is_update": is_update, "first_week_day": first_week_day},
                                     callback=self.parse_item, dont_filter=True)

    def parse_item(self, response):
        # 创建item
        item = DWDecspiderItem()
        item["msg"] = response.meta.get("data")
        item["is_update"] = response.meta.get("is_update")
        item["first_week_day"] = response.meta.get("first_week_day")
        # 解析返回json数据
        try:
            rs = json.loads(response.text)
            item["all_info"] = rs.get("data").get("preDecHeadVo")
            assert item.get("all_info", None), "未查到数据"
            yield item
        except json.decoder.JSONDecodeError as e:
            log.error(f'dw-url: {response.request.url} de 返回值有问题：{response.text}， {traceback.format_exc()}')
            raise e

