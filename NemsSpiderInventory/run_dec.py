"""
Description:
Author: song bo
Action      Date        Content
------------------------------------
Create      2019-
"""
import datetime
import os
import traceback
from multiprocessing import Process
import time

import pymongo
from scrapy import cmdline

from NemsSpider.utils.aniusql import sql, aniu_atomic
from NemsSpider.utils.login import Login

from NemsSpider.utils.log import getlogger

log = getlogger(__name__)


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

        if now_hour == 22 and now.weekday() == 6 and now.strftime("%Y%m%d") != "20190630":
            # 每周日22:00更新上周核注清单数据
            input_date = [
                {"inputDateStart": (now - datetime.timedelta(days=now.weekday()+7)).strftime("%Y%m%d"),
                 "inputDateEnd": (now - datetime.timedelta(days=now.weekday()+1)).strftime("%Y%m%d")}
            ]
            p = Process(target=run_spider, args=(input_date, False), daemon=True)
            p.start()
        # 每天核注清单数据每小时更新一次（更新时间段：8：00-22：00）
        if 8 <= now_hour <= 22:
            input_date = [
                {"inputDateStart": datetime.datetime.today().strftime("%Y%m%d"),
                 "inputDateEnd": datetime.datetime.today().strftime("%Y%m%d")}
            ]
            p = Process(target=run_spider, args=(input_date,), daemon=True)
            p.start()
            time.sleep(60 * 60)
        else:
            time.sleep(60 * 60 * 12)


def run_spider(input_date, is_today=True):
    # now_hour = int(datetime.datetime.now().strftime("%H"))
    # name = 'task[%d]' % os.getpid()
    # print(f'{now_hour}的任务：{name} start 跑起来')
    # a = Login("机保")
    # a.start_requests()
    # # os.system(f'scrapy crawl nems -a input_date={input_date} -a is_today={is_today}')
    cmdline.execute(['scrapy', 'crawl', '-a', f'input_date={input_date}', '-a', f'is_today={is_today}', 'nems'])


class NemsMongoToMysql(object):

    def __init__(self):
        self.sql = sql
        self.client = pymongo.MongoClient(host='172.18.2.193', port=27017)["Nems"]["20190701"]

    def process_main(self):
        all_info = self.client.find()  # 返回结果是Cursor类型，相当于一个生成器，我们需要遍历取到所有的结果，每一个结果都是字典类型。
        for item in all_info:
            seq_no = item.get("msg").get("QpSeqNo")
            nrelation = self.sql.select("NRelation", "id", where={"QpSeqNo": seq_no, "DeleteFlag": 0}, first=True)
            snrelation = self.sql.select("SpiderNRelation1", "id", where={"QpSeqNo": seq_no, "DeleteFlag": 0}, first=True)
            if nrelation or snrelation:
                print(f"跳过数据成功{seq_no}")
                continue
            try:
                with aniu_atomic(self.sql):
                    # Sadd 命令将一个或多个成员元素加入到集合中，已经存在于集合的成员元素将被忽略。
                    # 假如集合 key 不存在，则创建一个只包含添加的元素作成员的集合。当集合 key 不是集合类型时，返回一个错误。
                    # 说明是新增的记录
                    ret = self.sql.insert("SpiderNRelation1", **item.get("msg"))
                    # 新增表头
                    Nid = ret.id
                    # 处理表头 首字符大写
                    header_info = self.process_headers(item.get("headers"))
                    header_info["NId"] = Nid
                    self.sql.insert("SpiderNemsInvtHeadType1", **header_info)

                    # 处理表体
                    for one_list in item.get("lists"):
                        list_info = self.process_lists(one_list)
                        list_info["NId"] = Nid
                        self.sql.insert("SpiderNemsInvtListType1", **list_info)
                    print(f"插入数据成功{seq_no}")
            except Exception as e:
                log.error(traceback.format_exc())
                log.error("插入数据失败:{}".format(seq_no))
                raise e

    def process_headers(self, headers):
        headers_fields = {
            'bondInvtNo': 'BondInvtNo',
            'seqNo': 'SeqNo',
            'chgTmsCnt': 'ChgTmsCnt',
            'putrecNo': 'PutrecNo',
            'etpsInnerInvtNo': 'EtpsInnerInvtNo',
            'bizopEtpsSccd': 'BizopEtpsSccd',
            'bizopEtpsno': 'BizopEtpsno',
            'bizopEtpsNm': 'BizopEtpsNm',
            'rcvgdEtpsno': 'RcvgdEtpsno',
            'rvsngdEtpsSccd': 'RvsngdEtpsSccd',
            'rcvgdEtpsNm': 'RcvgdEtpsNm',
            'dclEtpsSccd': 'DclEtpsSccd',
            'dclEtpsno': 'DclEtpsno',
            'dclEtpsNm': 'DclEtpsNm',
            'invtDclTime': 'InvtDclTime',
            'entpyDclTime': 'EntpyDclTime',
            'entpyNo': 'EntpyNo',
            'rltInvtNo': 'RltInvtNo',
            'rltPutrecNo': 'RltPutrecNo',
            'rltEntryNo': 'RltEntryNo',
            'rltEntryBizopEtpsSccd': 'RltEntryBizopEtpsSccd',
            'rltEntryBizopEtpsno': 'RltEntryBizopEtpsno',
            'rltEntryBizopEtpsNm': 'RltEntryBizopEtpsNm',
            'rltEntryRvsngdEtpsSccd': 'RltEntryRvsngdEtpsSccd',
            'rltEntryRcvgdEtpsNo': 'RltEntryRcvgdEtpsNo',
            'rltEntryRcvgdetpsNm': 'RltEntryRcvgdetpsNm',
            'rltEntryDclEtpsSccd': 'RltEntryDclEtpsSccd',
            'rltEntryDclEtpsno': 'RltEntryDclEtpsno',
            'rltEntryDclEtpsNm': 'RltEntryDclEtpsNm',
            'impexpPortcd': 'ImpexpPortcd',
            'dclPlcCuscd': 'DclPlcCuscd',
            'impexpMarkcd': 'ImpexpMarkcd',
            'mtpckEndprdMarkcd': 'MtpckEndprdMarkcd',
            'supvModecd': 'SupvModecd',
            'trspModecd': 'TrspModecd',
            'dclcusFlag': 'DclcusFlag',
            'dclcusTypecd': 'DclcusTypecd',
            'vrfdedMarkcd': 'VrfdedMarkcd',
            'invtIochkptStucd': 'InvtIochkptStucd',
            'prevdTime': 'PrevdTime',
            'formalVrfdedTime': 'FormalVrfdedTime',
            'applyNo': 'ApplyNo',
            'listType': 'ListType',
            'inputCode': 'InputCode',
            'inputCreditCode': 'InputCreditCode',
            'inputName': 'InputName',
            'icCardNo': 'IcCardNo',
            'inputTime': 'InputTime',
            'listStat': 'ListStat',
            'corrEntryDclEtpsSccd': 'CorrEntryDclEtpsSccd',
            'corrEntryDclEtpsno': 'CorrEntryDclEtpsno',
            'corrEntryDclEtpsNm': 'CorrEntryDclEtpsNm',
            'decType': 'DecType',
            'addTime': 'AddTime',
            'stshipTrsarvNatcd': 'StshipTrsarvNatcd',
            'bondInvtTypecd': 'BondInvtTypecd',
            'entpyStucd': 'EntpyStucd',
            'passPortUsedTypecd': 'PassPortUsedTypecd',
            'rmk': 'Rmk',
            'dataState': 'DataState',
            'delcareFlag': 'DelcareFlag'}
        last_info = {headers_fields.get(key): headers.get(key) for key in set(headers_fields) & set(headers)}
        last_info["BondInvtTypecd"] = headers.get("invtType") or ""
        return last_info

    def process_lists(self, one_list):
        # tran_key = {
        #     "invtType": "BondInvtTypecd"
        # }
        list_fields = {
            'seqNo': 'SeqNo',
            'gdsSeqno': 'GdsSeqno',
            'putrecSeqno': 'PutrecSeqno',
            'gdsMtno': 'GdsMtno',
            'gdecd': 'Gdecd',
            'gdsNm': 'GdsNm',
            'gdsSpcfModelDesc': 'GdsSpcfModelDesc',
            'dclUnitcd': 'DclUnitcd',
            'lawfUnitcd': 'LawfUnitcd',
            'secdLawfUnitcd': 'SecdLawfUnitcd',
            'natcd': 'Natcd',
            'dclUprcAmt': 'DclUprcAmt',
            'dclTotalAmt': 'DclTotalAmt',
            'usdStatTotalAmt': 'UsdStatTotalAmt',
            'dclCurrcd': 'DclCurrcd',
            'lawfQty': 'LawfQty',
            'secdLawfQty': 'SecdLawfQty',
            'wtSfVal': 'WtSfVal',
            'fstSfVal': 'FstSfVal',
            'secdSfVal': 'SecdSfVal',
            'dclQty': 'DclQty',
            'grossWt': 'GrossWt',
            'netWt': 'NetWt',
            'useCd': 'UseCd',
            'lvyrlfModecd': 'LvyrlfModecd',
            'ucnsVerno': 'UcnsVerno',
            'entryGdsSeqno': 'EntryGdsSeqno',
            'clyMarkcd': 'ClyMarkcd',
            'flowApplyTbSeqno': 'FlowApplyTbSeqno',
            'applyTbSeqno': 'ApplyTbSeqno',
            'addTime': 'AddTime',
            'actlPassQty': 'ActlPassQty',
            'passPortUsedQty': 'PassPortUsedQty',
            'rmk': 'Rmk',
            'deleteFlag': 'DeleteFlag',
            'nId': 'NId',
            'yINUM': 'YINUM',
            'yENUM': 'YENUM',
            'zINUM': 'ZINUM',
            'zENUM': 'ZENUM',
            'iNVENTORYNUM': 'INVENTORYNUM',
            'dECLARENUM': 'DECLARENUM'}
        last_info = {list_fields.get(key): one_list.get(key) for key in set(list_fields) & set(one_list)}

        return last_info


if __name__ == '__main__':

    # input_date = [{"inputDateStart": "20190708", "inputDateEnd": "20190713"}]
    # cmdline.execute(['scrapy', 'crawl', '-a', f'input_date={input_date}', '-a', f'is_today=False', 'nems'])
    # a = Login("dec")
    # a.start_requests()
    # a = Login("nems")
    # a.start_requests()

    input_date = [{"updateTime": "2019-08-06", "updateTimeEnd": "2019-08-06"}]
    cmdline.execute(['scrapy', 'crawl', '-a', f'input_date={input_date}', '-a', f'is_today=False', 'dec'])
    # time.sleep(60*43)
    # run()
