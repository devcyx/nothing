# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import copy
import datetime
import traceback

import pymongo

from NemsSpider import settings
from NemsSpider.items import NemsspiderItem, DecspiderItem, DWDecspiderItem
from NemsSpider.utils.aniusql import sql, aniu_atomic, dw_sql
from NemsSpider.utils.redis_app import RedisApp
from NemsSpider.utils.log import getlogger

from NemsSpider.nems_join import InventoryNemsData, InventoryNemsDataCreate
log = getlogger(__name__)


class NemsspiderMyMongoPipeline(object):
    now = datetime.datetime.now()
    first_week_day = (now - datetime.timedelta(days=now.weekday())).strftime("%Y%m%d")  # 本周第一天
    client = pymongo.MongoClient(host=settings.MONGO_HOST, port=settings.MONGO_PORT)

    def process_item(self, item, spider):
        item_dict = copy.deepcopy(dict(item))
        is_update = item_dict.pop("is_update")
        first_week_day = item_dict.pop("first_week_day")
        if isinstance(item, NemsspiderItem):
            collection = self.client["Nems"][first_week_day]
            seqNo = item_dict.get("headers").get("seqNo")
            # if is_update:
            # 先删除在新增
            collection.delete_many({"msg.QpSeqNo": seqNo})
            collection.insert_one(item_dict)
        elif isinstance(item, DecspiderItem):
            collection = self.client["Dec"][first_week_day]
            QpEntryId = item_dict.get("msg").get("QpEntryId")
            # if is_update:
            # 先删除在新增
            collection.delete_many({"msg.QpEntryId": QpEntryId})
            collection.insert_one(item_dict)
        elif isinstance(item, DWDecspiderItem):
            collection = self.client["DWDec"][first_week_day]
            QpEntryId = item_dict.get("msg").get("QpEntryId")
            # if is_update:
            # 先删除在新增
            collection.delete_many({"msg.QpEntryId": QpEntryId})
            collection.insert_one(item_dict)
        return item


class NemsspiderMongoPipeline(object):
    client = pymongo.MongoClient(host=settings.MONGO_HOST, port=settings.MONGO_PORT)

    def process_item(self, item, spider):
        item.pop("is_update")
        item.pop("first_week_day")
        if isinstance(item, NemsspiderItem):
            collection = self.client["Nems"]["old"]
            collection.insert_one(dict(item))

        elif isinstance(item, DecspiderItem):
            collection = self.client["Dec"]["old"]
            collection.insert_one(dict(item))

        return item


class NemsspiderMysqlPipeline(object):
    pyredis = RedisApp().get_redis_instance()
    decid = None

    def open_spider(self, spider):
        """
        :Author: song bo
        :Date: 2019/3/11 13:45
        :Description: 爬虫开始时执行一次  进行初始化
        """
        self.sql = sql
        self.dw_sql = dw_sql

    def process_item(self, item, spider):
        """
        :Author: song bo
        :Date: 2019/3/11 13:45
        :Description: 存入数据看
        """
        item_dict = copy.deepcopy(dict(item))
        item_dict.pop("is_update")
        item_dict.pop("first_week_day")
        if isinstance(item, NemsspiderItem):
            return self.handler_nems(item_dict)
        if isinstance(item, DecspiderItem):
            dec = DecData(self.sql, "jibao")
            return dec.handler_dec(item_dict)
        if isinstance(item, DWDecspiderItem):
            dec = DecData(self.dw_sql, "dongguan")
            return dec.handler_dec(item_dict)

    def close_spider(self, spider):
        """
        :Author: song bo
        :Date: 2019/3/11 13:45
        :Description: 爬虫结束时执行一次
        """
        self.sql.cursor.close()
        self.sql.conn.close()

    def handler_nems(self, item):
        seq_no = item.get("headers").get("seqNo")
        try:
            with aniu_atomic(self.sql):
                # 处理表头 首字符大写
                nrelation = self.sql.select("ScrapyNRelation", "id", where={"QpSeqNo": seq_no, "DeleteFlag": 0}, first=True)
                """ 库存逻辑添加 by  Allen 19/7/22 开始"""
                self.data = {}
                data_list = []
                self.data['head_data'] = self.process_nems_headers(item.get("headers"))
                for one_list in item.get("lists"):
                    print("one_list", one_list)
                    list_info = self.process_nems_lists(one_list)
                    data_list.append(list_info)
                self.data['list_data'] = data_list
                self.data['msg_data'] = item.get("msg")
                # todo 这里需要分逻辑， 有直接入库的，有更新状态的（19.7.26）

                """ end """
                if nrelation:
                    # 修改更新状态,
                    print("更新 ")
                    try:
                        # 更新的时候状态也会得到更新, 这里需要随着状态的更新而变化库存数据
                        InventoryNemsData(nrelation.get("id"), self.data)
                        self.sql.update("ScrapyNRelation", **item.get("msg"),
                                        where={"QpSeqNo": seq_no, "DeleteFlag": 0})
                        log.info(f"已更新核注清单数据{seq_no}")
                        print(f"已更新核注清单数据{seq_no}")
                    except Exception as e:
                        print(e)
                        print(traceback.format_exc())
                        log.error(traceback.format_exc())
                        import time
                        time.sleep(3600)

                else:
                    print("创建")
                    try:
                        new_data_list = InventoryNemsDataCreate(self.data)
                        self.insert_nems_info(item, new_data_list)
                        log.info(f"已创建核注清单数据{seq_no}")
                        print(f"已创建核注清单数据{seq_no}")
                    except Exception as e:
                        print(e)
                        print(traceback.format_exc())
                        log.error(traceback.format_exc())
                        import time
                        time.sleep(3600)
            return item
        except Exception as e:
            log.error(traceback.format_exc())
            log.error(f"插入核注清单数据失败, 核注清单统一编号:{seq_no}")
            raise e

    def process_nems_headers(self, headers):
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

    def process_nems_lists(self, one_list):
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
            'dECLARENUM': 'DECLARENUM',
            'param3': 'Param3',
            'monitoringCondition': "MonitoringCondition",
            "quarantinCategory": "QuarantinCategory",
        }
        last_info = {list_fields.get(key): one_list.get(key) for key in set(list_fields) & set(one_list)}

        return last_info

    def insert_nems_info(self, item, new_data_list):
        """

        :param item:
        :return:
        """
        # 说明是新增的记录
        ret = self.sql.insert("ScrapyNRelation", **item.get("msg"))
        # 新增表头
        Nid = ret.id
        header_info = self.process_nems_headers(item.get("headers"))
        header_info["NId"] = Nid
        self.sql.insert("ScrapyNemsInvtHeadType", **header_info)
        # 处理表体
        for one_list in new_data_list.list_s: # 这里要将算好的库存与数据一起入库
        # for one_list in item.get("lists"):
        #     list_info = self.process_nems_lists(one_list)
            list_info = one_list
            list_info["NId"] = Nid
            self.sql.insert("ScrapyNemsInvtListType", **list_info)
            print("表体数据入库成功")

class DecData(object):

    def __init__(self, sql, flag):
        self.sql = sql
        self.flag = flag

    def handler_dec(self, item):
        seq_no = item.get("msg").get("QpSeqNo")
        if self.flag == "jibao" and self.sql.select("DecMsg", "decid", where={"QpSeqNo": seq_no, "DeleteFlag": 0},
                                                    first=True):
            print(f"jibao-已跳过报关单数据{seq_no}")
            log.warning(f"{self.flag}-已跳过报关单数据{seq_no}")
            return item  # 如果是gmb申报的单  不进行入库
        try:
            with aniu_atomic(self.sql):
                # 处理表头 首字符大写
                self.decid = self.sql.select("ScrapyDecMsg", "decid", where={"QpSeqNo": seq_no, "DeleteFlag": 0},
                                             first=True)
                if self.decid:
                    # 修改更新状态
                    self.sql.update("ScrapyDecMsg", **item.get("msg"), where={"QpSeqNo": seq_no, "DeleteFlag": 0})
                    log.info(f"{self.flag}-已更新报关单数据{seq_no}")
                    print(f"{self.flag}-已更新报关单数据{seq_no}")
                else:
                    self.insert_dec_info(item)
                    log.info(f"{self.flag}-已新增报关单数据{seq_no}")
                    print(f"{self.flag}-已新增报关单数据{seq_no}")
            return item
        except Exception as e:
            log.error(traceback.format_exc())
            log.error(f"{self.flag}-插入报关单数据失败，报关单统一编号：{seq_no}")
            raise e

    def insert_dec_info(self, item):
        ret = self.sql.insert("ScrapyDecMsg", **item.get("msg"))
        # 新增表头
        self.decid = ret.id
        all_info = item.get("all_info")
        # 处理表头 首字符大写
        self.process_dec_headers(all_info)

        # 集装箱
        if all_info.get("preDecContainerVo"):
            container_dict = {
                "lclFlag": "LclFlag"
                , "goodsNo": "GoodsNo"
                , "containerNo": "ContainerId"
                , "containerMdCode": "ContainerMd"
                , "containerWt": "ContainerWt"
            }
            self.insert_dec_other(container_dict, all_info.pop("preDecContainerVo"), "ScrapyDecContainer")
        # DecCopLimit
        if all_info.get("preDecEntQualifListVo"):
            coplimit_dict = {
                "entQualifNo": "EntQualifNo"
                , "entQualifTypeCode": "EntQualifTypeCode"
            }
            self.insert_dec_other(coplimit_dict, all_info.pop("preDecEntQualifListVo"), "ScrapyDecCopLimit")
        # 自由文本
        freetxt_dict = {
            "bonNo": "BonNo"
            , "cusFie": "CusFie"
            , "decBpNo": "DecBpNo"
            , "decNo": "DecNo"
            , "relId": "RelId"
            , "relManNo": "RelManNo"
            , "cusVoyageNo": "VoyNo"
        }
        self.insert_dec_data(freetxt_dict, all_info, "ScrapyDecFreeTxt")
        # 随附单证
        if all_info.get("cusLicenseListVo"):
            licensedoc_dict = {
                "acmpFormCode": "DocuCode"
                , "acmpFormNo": "CertCode"
            }
            self.insert_dec_other(licensedoc_dict, all_info.get("cusLicenseListVo"), "ScrapyDecLicenseDoc")
        # 随附单证
        if all_info.get("decOtherPacksVo"):
            otherpack_dict = {
                "packType": "PackType"
                , "packQty": "PackQty"
            }
            self.insert_dec_other(otherpack_dict, all_info.get("decOtherPacksVo"), "ScrapyDecOtherPack")
        # 申请单证信息
        if all_info.get("preDecRequCertList"):
            requ_dict = {
                "appCertCode": "AppCertCode"
                , "applOri": "ApplOri"
                , "applCopyQuan": "ApplCopyQuan"
            }
            self.insert_dec_other(requ_dict, all_info.get("preDecRequCertList"), "ScrapyDecRequestCert")
        # 使用人
        if all_info.get("preDecUserList"):
            user_dict = {
                "useOrgPersonCode": "UseOrgPersonCode"
                , "useOrgPersonTel": "UseOrgPersonTel"
            }
            self.insert_dec_other(user_dict, all_info.get("preDecUserList"), "ScrapyDecUser")
        # 处理表体
        for one_list in eval(all_info.get("decMergeListVo")):
            self.process_dec_lists(one_list)

    def process_dec_headers(self, headers):
        headers_fields = {
            'spDecSeqNo': 'SeqNo',
            'cusIEFlag': 'IEFlag',
            'agentCode': 'AgentCode',
            'agentName': 'AgentName',
            'apprNo': 'ApprNo',
            'billNo': 'BillNo',
            'contrNo': 'ContrNo',
            'customMaster': 'CustomMaster',
            'cutMode': 'CutMode',
            'distinatePort': 'DistinatePort',
            'feeCurr': 'FeeCurr',
            'feeMark': 'FeeMark',
            'feeRate': 'FeeRate',
            'grossWt': 'GrossWet',
            'iEDate': 'IEDate',
            'iEPort': 'IEPort',
            'insurCurr': 'InsurCurr',
            'insurMark': 'InsurMark',
            'insurRate': 'InsurRate',
            'licenseNo': 'LicenseNo',
            'manualNo': 'ManualNo',
            'netWt': 'NetWt',
            'noteS': 'Notes',
            'otherCurr': 'OtherCurr',
            'otherMark': 'OtherMark',
            'otherRate': 'OtherRate',
            'ownerCode': 'OwnerCode',
            'ownerName': 'OwnerName',
            'packNo': 'PackNo',
            'cusTradeCountry': 'TradeCountry',
            'supvModeCdde': 'TradeMode',
            'cusTrafMode': 'TrafMode',
            'trafName': 'TrafName',
            'transMode': 'TransMode',
            'wrapType': 'WrapType',
            'entryId': 'EntryId',
            'preEntryId': 'PreEntryId',
            'ediId': 'EdiId',
            'risk': 'Risk',
            'copName': 'CopName',
            'copCode': 'CopCode',
            'entryType': 'EntryType',
            'pDate': 'PDate',
            'typistNo': 'TypistNo',
            'inputerName': 'InputerName',
            'partenerID': 'PartenerID',
            'tgdNo': 'TgdNo',
            'dataSource': 'DataSource',
            'declTrnRel': 'DeclTrnRel',
            'chkSurety': 'ChkSurety',
            'billType': 'BillType',
            'agentScc': 'AgentCodeScc',
            'ownerScc': 'OwnerCodeScc',
            'copCodeScc': 'CopCodeScc',
            'promiseItems': 'PromiseItmes',
            'cusTradeNationCode': 'TradeAreaCode',
            'markNo': 'MarkNo',
            'checkFlow': 'CheckFlow',
            'taxAaminMark': 'TaxAaminMark',
            'despPortCode': 'DespPortCode',
            'goodsPlace': 'GoodsPlace',
            'bLNo': 'BLNo',
            'inspOrgCode': 'InspOrgCode',
            'purpOrgCode': 'PurpOrgCode',
            'despDate': 'DespDate',
            'correlationReasonFlag': 'CorrelationReasonFlag',
            'vsaOrgCode': 'VsaOrgCode',
            'orgCode': 'OrgCode',
            'domesticConsigneeEname': 'DomesticConsigneeEname',
            'correlationNo': 'CorrelationNo',
            'specDeclFlag': 'SpecDeclFlag',
            'type': 'Type',
            'tradeCiqCode': 'TradeCiqCode',
            'ownerCiqCode': 'OwnerCiqCode',
            'declCiqCode': 'DeclCiqCode',
            'origBoxFlag': 'OrigBoxFlag',
            'declaratioMaterialCode': 'DeclaratioMaterialCode'
        }
        if headers.get("cusIEFlag") == "E":
            ie_dict = {
                "cnsnTradeCode": "TradeCode",
                "cnsnTradeScc": "tradeCoScc",
                "consignorCname": "TradeName",
                'despPortCode': 'EntyPortCode',
                'consigneeEname': 'OverseasConsigneeEname',
                'consigneeCode': 'OverseasConsigneeCode',
            }
        else:
            ie_dict = {
                "rcvgdTradeCode": "TradeCode",
                "rcvgdTradeScc": "tradeCoScc",
                "consigneeCname": "TradeName",
                'ciqEntyPortCode': 'EntyPortCode',
                'consignorCname': 'OverseasConsignorCname',
                'consignorEname': 'OverseasConsignorEname',
                'consignorCode': 'OverseasConsignorCode',
            }
        headers_fields.update(ie_dict)
        header_info = {val: headers.get(key) for key, val in headers_fields.items() if headers.get(key)}
        if header_info.get("DespDate"):
            header_info["DespDate"] = header_info.get("DespDate").replace("-", "")
        header_info["DecId"] = self.decid
        self.sql.insert("ScrapyDecHead", **header_info)

    def process_dec_lists(self, one_list):
        list_fields = {
            "gNo": "GNo"
            , "classMark": "ClassMark"
            , "codeTs": "CodeTs"
            , "contrItem": "ContrItem"
            , "declPrice": "DeclPrice"
            , "dutyMode": "DutyMode"
            , "factor": "Factor"
            , "gModel": "GModel"
            , "gName": "GName"
            , "cusOriginCountry": "OriginCountry"
            , "tradeCurr": "TradeCurr"
            , "declTotal": "DeclTotal"
            , "gQty": "GQty"
            , "qty1": "FirstQty"
            , "qty2": "SecondQty"
            , "gUnit": "GUnit"
            , "unit1": "FirstUnit"
            , "unit2": "SecondUnit"
            , "useTo": "UseTo"
            , "workUsd": "WorkUsd"
            , "exgNo": "ExgNo"
            , "exgVersion": "ExgVersion"
            , "destinationCountry": "DestinationCountry"
            , "ciqName": "CiqName"
            , "goodsAttr": "GoodsAttr"
            , "stuff": "Stuff"
            , "prodValidDt": "ProdValidDt"
            , "prodQgp": "ProdQgp"
            , "engManEntCnm": "EngManEntCnm"
            , "goodsSpec": "GoodsSpec"
            , "goodsModel": "GoodsModel"
            , "goodsBrand": "GoodsBrand"
            , "produceDate": "ProduceDate"
            , "prodBatchNo": "ProdBatchNo"
            , "purpose": "Purpose"
            , "origPlaceCode": "OrigPlaceCode"
            , "ciqCode": "CiqCode"
            , "districtCode": "DistrictCode"
            , "noDangFlag": "NoDangFlag"
            , "unCode": "UnCode"
            , "dangName": "DangName"
            , "dangPackType": "DangPackType"
            , "dangPackSpec": "DangPackSpec"
            , "ciqDestCode": "DestCode"
        }
        last_info = {val: one_list.get(key) for key, val in list_fields.items() if one_list.get(key)}
        last_info["DeleteFlag"] = 0
        last_info["DecId"] = self.decid
        ret = self.sql.insert("ScrapyDeclist", **last_info)
        # 许可证
        data = eval(one_list.get("preDecCiqGoodsLimit"))
        if data:
            for one_data in data:
                limit_dict = {
                    "gNo": "GoodsNo"
                    , "licTypeCode": "LicTypeCode"
                    , "licenceNo": "LicenceNo"
                    , "licWrtofDetailNo": "LicWrtofDetailNo"
                    , "licWrtofUnit": "LicWrtofQty"
                }
                data_info = {val: one_data.get(key) for key, val in limit_dict.items() if one_data.get(key)}
                data_info["DeleteFlag"] = 0
                data_info["DecListId"] = ret.id
                self.sql.insert("ScrapyDecGoodsLimit", **data_info)
        return last_info

    def insert_dec_other(self, key_dict, data_list, table):
        for data in eval(data_list):
            self.insert_dec_data(key_dict, data, table)

    def insert_dec_data(self, key_dict, data, table):
        data_info = {val: data.get(key) for key, val in key_dict.items() if data.get(key)}
        if data_info:
            data_info["DeleteFlag"] = 0
            data_info["DecId"] = self.decid
            self.sql.insert(table, **data_info)
