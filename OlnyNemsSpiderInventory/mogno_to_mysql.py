"""
Description:
Author: song bo
Action      Date        Content
------------------------------------
Create      2019-
"""
import datetime
import traceback

import pymongo

from NemsSpider.utils.aniusql import sql, aniu_atomic
from NemsSpider.utils.log import getlogger

log = getlogger(__name__)


class NemsMongoToMysql(object):

    def __init__(self):
        self.sql = sql
        self.client = pymongo.MongoClient(host='172.18.2.193', port=27017)["Nems"]["20190715"]

    def process_main(self):
        all_info = self.client.find()  # 返回结果是Cursor类型，相当于一个生成器，我们需要遍历取到所有的结果，每一个结果都是字典类型。
        for item in all_info:
            seq_no = item.get("msg").get("QpSeqNo")
            snrelation = self.sql.select("ScrapyNRelation", "id", where={"QpSeqNo": seq_no, "DeleteFlag": 0}, first=True)
            if snrelation:
                print(f"跳过数据成功{seq_no}")
                continue
            try:
                with aniu_atomic(self.sql):
                    # Sadd 命令将一个或多个成员元素加入到集合中，已经存在于集合的成员元素将被忽略。
                    # 假如集合 key 不存在，则创建一个只包含添加的元素作成员的集合。当集合 key 不是集合类型时，返回一个错误。
                    # 说明是新增的记录
                    ret = self.sql.insert("ScrapyNRelation", **item.get("msg"))
                    # 新增表头
                    Nid = ret.id
                    # 处理表头 首字符大写
                    header_info = self.process_headers(item.get("headers"))
                    header_info["NId"] = Nid
                    self.sql.insert("ScrapyNemsInvtHeadType", **header_info)

                    # 处理表体
                    for one_list in item.get("lists"):
                        list_info = self.process_lists(one_list)
                        list_info["NId"] = Nid
                        self.sql.insert("ScrapyNemsInvtListType", **list_info)
                    # print(f"插入数据成功{seq_no}")
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


class DecMongoToMysql(object):

    def __init__(self):
        self.sql = sql
        self.client = pymongo.MongoClient(host='172.18.2.193', port=27017)["Dec"]["old"]
        self.decid = None

    def process_main(self):
        all_info = self.client.find().skip(49110)  # 返回结果是Cursor类型，相当于一个生成器，我们需要遍历取到所有的结果，每一个结果都是字典类型。
        for item in all_info:
            seq_no = item.get("msg").get("QpSeqNo")
            decid = self.sql.select("DecMsg", "decid", where={"QpSeqNo": seq_no, "DeleteFlag": 0}, first=True)
            sdecid = self.sql.select("ScrapyDecMsg", "decid", where={"QpSeqNo": seq_no, "DeleteFlag": 0}, first=True)
            if decid or sdecid:
                print(f"跳过数据成功{seq_no}")
                continue
            try:
                with aniu_atomic(self.sql):
                    # Sadd 命令将一个或多个成员元素加入到集合中，已经存在于集合的成员元素将被忽略。
                    # 假如集合 key 不存在，则创建一个只包含添加的元素作成员的集合。当集合 key 不是集合类型时，返回一个错误。
                    # 说明是新增的记录
                    ret = self.sql.insert("ScrapyDecMsg", **item.get("msg"))
                    # 新增表头
                    self.decid = ret.id
                    all_info = item.get("all_info")
                    # 处理表头 首字符大写
                    self.process_headers(all_info)

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
                        self.process_lists(one_list)
                    print(f"插入数据成功{seq_no}")
            except Exception as e:
                log.error(traceback.format_exc())
                # log.error("插入数据失败".format(seq_no))
                print(all_info)
                raise e

    def process_headers(self, headers):
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

    def process_lists(self, one_list):
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


if __name__ == '__main__':
    a = NemsMongoToMysql()
    a.process_main()
