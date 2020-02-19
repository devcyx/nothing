# !/usr/bin/env python
# coding: utf-8
"""
Description: 针对库存进行计算
Author: allen
Date: 19/7/22
"""

# from spider.models import NewsInvtStatistics, SpiderNRelation,ScrapyNemsInvtHeadType,ScrapyNemsInvtListType

from NemsSpider import settings
from NemsSpider.utils.log import getlogger
from NemsSpider.utils.aniusql import Sql
from decimal import Decimal

logger = getlogger(__name__)


class InventoryNemsData(object):
    def __init__(self, id, item):
        self.id = id
        self.item = item
        self.msg_s = item.get("msg_data")
        self.head_s = item.get('head_data')
        self.list_s = item.get('list_data')
        self.get_sql_data()

    def get_sql_data(self):
        self.sql = Sql(settings.DATABASES)
        print("self.id", self.id)
        self.msg_data = self.sql.select("ScrapyNRelation", where={"id": self.id, "DeleteFlag": 0}, first=True)
        print("self.msg_data", self.msg_data)
        self.head_data = self.sql.select("ScrapyNemsInvtHeadType", where={"NId": self.id}, first=True)
        self.list_data = self.sql.select("ScrapyNemsInvtListType", where={"NId": self.id, "DeleteFlag": 0})

        # 这里针对不同的情况进行判断，对库存进行操作
        if self.msg_s.get('DecState') == 'CR_9' and self.head_s['VrfdedMarkcd'] == '2':  # 终审批通过,
            self.first_final_data()
        elif self.msg_s.get('DecState') == 'CR_4' and self.head_s['VrfdedMarkcd'] == '2':  # 预审批通过, 已核扣
            self.trial_batch_finally()
        elif self.msg_s.get('DecState') == 'CR_4' and (
                self.head_s['VrfdedMarkcd'] == '0' or self.head_s['VrfdedMarkcd'] == '1'):  # 预审批通过, 未核扣，预核扣
            self.trial_batch_begin()
        elif (self.msg_s.get('DecState') == 'CR_9' and self.head_s['VrfdedMarkcd'] == '2') or (
                self.msg_data.get('DecState') == 'CR_4' and self.head_data['VrfdedMarkcd'] == '2') and (
                self.msg_data.get('DecState') == 'CR_4' and (self.head_data['VrfdedMarkcd'] == '0' or self.head_data[
            'VrfdedMarkcd'] == '1')):  # 爬取的是总审批通过，已核扣， 更新之前的是 预审批通过，未核扣，预核扣 或者 爬取的预审批通过，已核扣
            # todo 这里需要重新组合数据
            self.double_state_chage()
        elif (self.msg_s.get('DecState') == 'CR_9' and
              self.head_s['VrfdedMarkcd'] == '2') or (self.msg_data.get('DecState') == 'CR_4' and self.head_data[
            'VrfdedMarkcd'] == '2'):  # # 爬取的是总审批通过，已核扣, 数据库是 预审批通过，已核扣
            pass  # 不做任何操作
            logger.error("爬取的是总审批通过，已核扣, 数据库是 预审批通过，已核扣{},{},{},{}".format(self.msg_s.get('DecState'), self.head_s['VrfdedMarkcd'],
                                                self.msg_data.get('DecState'), self.head_data['VrfdedMarkcd']))


        elif self.msg_s.get('DecState') == 'CR_9' and self.head_s['VrfdedMarkcd'] == '1':  # 爬起是终审批通过，未核扣
            self.last_undeductible()
        elif (self.msg_s.get('DecState') == 'CR_9' and self.head_s['VrfdedMarkcd'] == '2' and (
                self.msg_data.get('DecState') == 'CR_9' and self.head_data[
            'VrfdedMarkcd'] == '1')):  # 终审批通过，已核扣  -- 终审批通过 未核扣
            self.trial_batch_finally_join()
        else:
            logger.error("走的其他条件逻辑{},{},{},{}".format(self.msg_s.get('DecState'), self.head_s['VrfdedMarkcd'],
                                                self.msg_data.get('DecState'), self.head_data['VrfdedMarkcd']))

    def double_state_chage(self):
        """
        author: allen
        date: 19/7/26
        description: 海关总审批通过，未核扣
        :return:
        """
        for obj in self.list_s:
            data = {}
            inventory, YINUM, YENUM, ZINUM, ZENUM = self.data_clear_all(obj)
            if self.head_s.get("ImpexpMarkcd") == 'I':  # 进口
                ZINUM += Decimal(str(obj.get("DclQty")))
                YINUM -= Decimal(str(obj.get("DclQty")))
                if YINUM < 0:
                    logger.error("YINUM = {}, 这里不应该是负数".format(YINUM))
            elif self.head_s.get("ImpexpMarkcd") == 'E':  # 出口
                ZENUM += Decimal(str(obj.get("DclQty")))
                YENUM -= Decimal(str(obj.get("DclQty")))
                if YENUM < 0:
                    logger.error("YENUM = {}, 这里不应该是负数".format(YINUM))

            data['ZINUM'] = ZINUM
            data['ZENUM'] = ZENUM
            data['YINUM'] = YINUM
            data['YENUM'] = YENUM
            self.sql_operation(inventory, obj, data)

    def last_undeductible(self):
        """
                author: allen
                date: 19/7/26
                description: 海关总审批通过，未核扣
                :return:
                """
        for obj in self.list_s:
            data = {}
            inventory, YINUM, YENUM, ZINUM, ZENUM = self.data_clear_all(obj)
            if self.head_s.get("ImpexpMarkcd") == 'I':  # 进口
                pass
            elif self.head_s.get("ImpexpMarkcd") == 'E':  # 出口
                YENUM += Decimal(str(obj.get("DclQty")))

            data['ZINUM'] = ZINUM
            data['ZENUM'] = ZENUM
            data['YINUM'] = YINUM
            data['YENUM'] = YENUM
            self.sql_operation(inventory, obj, data)

    def data_clear_all(self, obj):
        """
            author: allen
            date: 19/7/22
            description: 对数据进行初始化
        """
        if obj.get('PutrecSeqno'):
            inventory = self.sql.select("NewsInvtStatistics", where={"GNO": obj.get('PutrecSeqno')}, first=True)
        else:
            inventory = self.sql.select("NewsInvtStatistics", where={"GNO": obj.get('Param3')}, first=True)
        YINUM = Decimal(str(inventory.get('YINUM'))) if inventory else 0  # 预增数量: 核注清单数据状态为预审批通过的进口保税核注清单备案序号申报数量
        YENUM = Decimal(str(inventory.get('YENUM'))) if inventory else 0  # 预扣数量：核注清单数据状态为预审批通过的出口保税核注清单备案序号申报数量
        ZINUM = Decimal(str(inventory.get('ZINUM'))) if inventory else 0  # 实增数量：核注清单数据状态为海关终审通过的进口保税核注清单备案序号申报数量
        ZENUM = Decimal(str(inventory.get('ZENUM'))) if inventory else 0  # 实扣数量：核注清单数据状态为海关终审通过的出口保税核注清单备案序号申报数量

        return inventory, YINUM, YENUM, ZINUM, ZENUM

    def sql_operation(self, inventory, obj, data):
        """
        author: allen
        date: 19/7/22
        description: 对数据存放在数据库中
        :param inventory:
        :param obj:
        :return:
        """
        datas = self.sql.select("Commodity", "monitoring_condition", "quarantine_category",
                               where={"codets": obj.get('Gdecd')},
                               first=True)
        print("datas",datas,type(datas))
        obj['MonitoringCondition'] = self.MonitoringCondition = datas.get("monitoring_condition")
        obj['QuarantinCategory'] = self.QuarantinCategory = datas.get("quarantine_category")
        INVENTORYNUM = data['ZINUM'] + data['YINUM'] - data['ZENUM'] - data['YENUM']  # 库存数量: 实增数量+预增数量-实扣数量-预扣数量
        DECLARENUM = data['ZINUM'] - data['ZENUM'] - data['YINUM']  # 可申报数量: 实增数量-实扣数量-预扣数量
        self.updata_list_data(data, INVENTORYNUM, DECLARENUM, obj, obj.get('PutrecSeqno'))
        # self.sql.update("ScrapyNemsInvtListType", **{
        #     "YINUM": data['YINUM'],
        #     "YENUM": data['YENUM'],
        #     "ZINUM": data['ZINUM'],
        #     "ZENUM": data['ZENUM'],
        #     "INVENTORYNUM": INVENTORYNUM,
        #     "DECLARENUM": DECLARENUM,
        #     "MonitoringCondition": obj.get("MonitoringCondition"),
        #     "QuarantinCategory": obj.get("QuarantinCategory")
        # }, where={"id": obj.get('id'), "DeleteFlag": 0})
        # logger.info("表体数据库存更新成功{},{}".format(obj.get("id"), obj.get('PutrecSeqno')))
        if inventory:
            if obj.get('PutrecSeqno'):
                self.updata_data(data, INVENTORYNUM, DECLARENUM, obj, obj.get('PutrecSeqno'))
                # self.sql.update("NewsInvtStatistics", **{
                #     "YINUM": data['YINUM'],
                #     "YENUM": data['YENUM'],
                #     "ZINUM": data['ZINUM'],
                #     "ZENUM": data['ZENUM'],
                #     "INVENTORYNUM": INVENTORYNUM,
                #     "DECLARENUM": DECLARENUM,
                #     "MonitoringCondition": obj.get("MonitoringCondition"),
                #     "QuarantinCategory": obj.get("QuarantinCategory")
                # }, where={"GNO": obj.get('PutrecSeqno')})
                # logger.info("备案序号数据更新成功{},{}".format(self.id, obj.get('PutrecSeqno')))
            else:
                # self.sql.update("NewsInvtStatistics", **{
                #     "YINUM": data['YINUM'],
                #     "YENUM": data['YENUM'],
                #     "ZINUM": data['ZINUM'],
                #     "ZENUM": data['ZENUM'],
                #     "INVENTORYNUM": INVENTORYNUM,
                #     "DECLARENUM": DECLARENUM,
                #     "MonitoringCondition": obj.get("MonitoringCondition"),
                #     "QuarantinCategory": obj.get("QuarantinCategory")
                # }, where={"GNO": obj.get('Param3')})
                # logger.info("备案序号数据更新成功{},{}".format(self.id, obj.get('Param3')))
                self.updata_data(data, INVENTORYNUM, DECLARENUM, obj, obj.get('Param3'))

        else:
            if obj.get('PutrecSeqno'):
                self.insert_data(data, INVENTORYNUM, DECLARENUM, obj, obj.get('PutrecSeqno'))
                # self.sql.insert("NewsInvtStatistics", **{
                #     "GNO": obj.get('PutrecSeqno'),
                #     "YINUM": data['YINUM'],
                #     "YENUM": data['YENUM'],
                #     "ZINUM": data['ZINUM'],
                #     "ZENUM": data['ZENUM'],
                #     "INVENTORYNUM": INVENTORYNUM,
                #     "DECLARENUM": DECLARENUM,
                #     "MonitoringCondition": obj.get("MonitoringCondition"),
                #     "QuarantinCategory": obj.get("QuarantinCategory")
                # }, )
                # logger.info("备案序号数据写入成功{}".format(obj.get('PutrecSeqno')))
            else:
                # self.sql.insert("NewsInvtStatistics", **{
                #     "GNO": obj.get('Param3'),
                #     "YINUM": data['YINUM'],
                #     "YENUM": data['YENUM'],
                #     "ZINUM": data['ZINUM'],
                #     "ZENUM": data['ZENUM'],
                #     "INVENTORYNUM": INVENTORYNUM,
                #     "DECLARENUM": DECLARENUM,
                #     "MonitoringCondition": obj.get("MonitoringCondition"),
                #     "QuarantinCategory": obj.get("QuarantinCategory")
                # }, )
                # logger.info("备案序号数据写入成功{}".format(obj.get('Param3')))
                self.insert_data(data, INVENTORYNUM, DECLARENUM, obj, obj.get('Param3'))

    def updata_list_data(self, data, INVENTORYNUM, DECLARENUM, obj, category):
        self.sql.update("ScrapyNemsInvtListType", **{
            "YINUM": data['YINUM'],
            "YENUM": data['YENUM'],
            "ZINUM": data['ZINUM'],
            "ZENUM": data['ZENUM'],
            "INVENTORYNUM": INVENTORYNUM,
            "DECLARENUM": DECLARENUM,
            "MonitoringCondition": self.MonitoringCondition,
            "QuarantinCategory": self.QuarantinCategory
        }, where={"id": obj.get('id'), "DeleteFlag": 0})
        logger.info("表体数据库存更新成功{},{}".format(obj.get("id"), category))

    def updata_data(self, data, INVENTORYNUM, DECLARENUM, obj, category):
        self.sql.update("NewsInvtStatistics", **{
            "YINUM": data['YINUM'],
            "YENUM": data['YENUM'],
            "ZINUM": data['ZINUM'],
            "ZENUM": data['ZENUM'],
            "INVENTORYNUM": INVENTORYNUM,
            "DECLARENUM": DECLARENUM,
            "MONITORING": self.MonitoringCondition,
            "QUARANTINE": self.QuarantinCategory
        }, where={"GNO": category})
        logger.info("备案序号数据更新成功{},{}".format(self.id, category))

    def insert_data(self, data, INVENTORYNUM, DECLARENUM, obj, category):
        # commodify_data = Commodity.objects.filter(codets=obj.Gdecd).first()
        # data['monitoring_condition'] = commodify_data.monitoring_condition
        # data['quarantine_category'] = commodify_data.quarantine_category

        self.sql.insert("NewsInvtStatistics", **{
            "GNO": category,
            "YINUM": data['YINUM'],
            "YENUM": data['YENUM'],
            "ZINUM": data['ZINUM'],
            "ZENUM": data['ZENUM'],
            "INVENTORYNUM": INVENTORYNUM,
            "DECLARENUM": DECLARENUM,
            "MONITORING": self.MonitoringCondition,
            "QUARANTINE": self.QuarantinCategory
        }, )
        logger.info("备案序号数据写入成功{}".format(category))

    def first_final_data(self):
        """
         author: allen
         date: 19/7/22
         description: 爬去数据直接是海关终审批通过
        :return:
        """

        for obj in self.list_s:
            data = {}
            inventory, YINUM, YENUM, ZINUM, ZENUM = self.data_clear_all(obj)
            # todo 直接是终审批通过, 不经过预审批操作
            if self.msg_s.get("DecState") == 'CR_9' and self.head_s['VrfdedMarkcd'] == '2':  # 终审批通过
                if self.head_s.get("ImpexpMarkcd") == 'I':  # 进口
                    ZINUM += Decimal(str(obj.get("DclQty")))
                    data['ZINUM'] = ZINUM
                    if ZINUM < 0:
                        logger.error("YINUM = {}, 这里不应该是负数".format(ZINUM))
                elif self.head_s.get("ImpexpMarkcd") == 'E':  # 出口k
                    ZENUM += Decimal(str(obj.get("DclQty")))
                    data['ZENUM'] = ZENUM
                    if ZENUM < 0:
                        logger.error("YENUM = {}, 这里不应该是负数".format(ZENUM))
                data['YINUM'] = YINUM
                data['YENUM'] = YENUM
                data['ZINUM'] = ZINUM
                data['ZENUM'] = ZENUM
                self.sql_operation(inventory, obj, data)

    def trial_batch_finally(self):
        """
         author: allen
         date: 19/7/22
         description: 爬去数据直接是预审批通过, 已核扣
        :return:
        """
        VrfdedMarkcd = self.head_s.get("VrfdedMarkcd")  # 核扣标记代码 0未核扣,1预核扣,2已核扣
        I_E_Port = self.head_s.get("ImpexpMarkcd")  # 进出口标志
        for obj in self.list_s:
            data = {}
            inventory, YINUM, YENUM, ZINUM, ZENUM = self.data_clear_all(obj)
            # todo 爬去数据直接是预审批通过, 已核扣
            if I_E_Port == 'I':  # 进口
                ZINUM += Decimal(str(obj.get("DclQty")))
            elif I_E_Port == 'E':  # 出口
                ZENUM += Decimal(str(obj.get("DclQty")))
            data['ZINUM'] = ZINUM
            data['ZENUM'] = ZENUM
            data['YINUM'] = YINUM
            data['YENUM'] = YENUM
            self.sql_operation(inventory, obj, data)

    def trial_batch_begin(self):
        """
         author: allen
         date: 19/7/22
         description: 爬去数据直接是预审批通过, 未核扣, 预核扣
        :return:
        """
        VrfdedMarkcd = self.head_s.get("VrfdedMarkcd")  # 核扣标记代码 0未核扣,1预核扣,2已核扣
        I_E_Port = self.head_s.get("ImpexpMarkcd")  # 进出口标志
        for obj in self.list_s:
            data = {}
            inventory, YINUM, YENUM, ZINUM, ZENUM = self.data_clear_all(obj)
            # todo 爬去数据直接是预审批通过, 未核扣, 预核扣
            if I_E_Port == 'I':  # 进口
                YINUM += Decimal(str(obj.get("DclQty")))
            elif I_E_Port == 'E':  # 出口
                YENUM += Decimal(str(obj.get("DclQty")))
            data['ZINUM'] = ZINUM
            data['ZENUM'] = ZENUM
            data['YINUM'] = YINUM
            data['YENUM'] = YENUM
            self.sql_operation(inventory, obj, data)

    def trial_batch_finally_join(self):
        """
         author: allen
         date: 19/7/22
         description: 爬去数据终审批通过, 未核扣-----终审批通过, 已核扣
        :return:
        """
        VrfdedMarkcd = self.head_s.get("VrfdedMarkcd")  # 核扣标记代码 0未核扣,1预核扣,2已核扣
        I_E_Port = self.head_s.get("ImpexpMarkcd")  # 进出口标志
        for obj in self.list_s:
            data = {}
            inventory, YINUM, YENUM, ZINUM, ZENUM = self.data_clear_all(obj)
            # todo 爬去数据终审批通过, 未核扣-----终审批通过, 已核扣
            if I_E_Port == 'I':  # 进口
                ZINUM += Decimal(str(obj.get("DclQty")))
            elif I_E_Port == 'E':  # 出口
                ZENUM += Decimal(str(obj.get("DclQty")))
                YENUM += Decimal(str(obj.get("DclQty")))
            data['ZINUM'] = ZINUM
            data['ZENUM'] = ZENUM
            data['YINUM'] = YINUM
            data['YENUM'] = YENUM
            self.sql_operation(inventory, obj, data)

    def normal_circumstances(self):
        """
        author: allen
        date: 19/7/18
        description: 此函数暂时没有用到
        :return:
        """
        for obj in self.list_data:
            data = {}
            inventory, YINUM, YENUM, ZINUM, ZENUM = self.data_clear_all(obj)
            VrfdedMarkcd = self.head_data.get("VrfdedMarkcd")  # 核扣标记代码 0未核扣,1预核扣,2已核扣
            I_E_Port = self.head_data.get("ImpexpMarkcd")  # 进出口标志
            # todo 这里需要分情况, 条件是按照正常流程走, 数据先是预审批通过,然后再是终审批通过
            if self.msg_data.get("DecState") == 'CR_9' and VrfdedMarkcd == '2':  # 终审批通过
                if I_E_Port == 'I':  # 进口
                    ZINUM += Decimal(str(obj.get("DclQty")))
                    YINUM -= Decimal(str(obj.get("DclQty")))
                    if YINUM < 0:
                        logger.error("YINUM = {}, 这里不应该是负数".format(YINUM))
                elif I_E_Port == 'E':  # 出口
                    ZENUM += Decimal(str(obj.get("DclQty")))
                    YENUM -= Decimal(str(obj.get("DclQty")))
                    if YENUM < 0:
                        logger.error("YENUM = {}, 这里不应该是负数".format(YINUM))
            elif self.msg_data.get("DecState") == 'CR_4' and (
                    VrfdedMarkcd == '0' or VrfdedMarkcd == '1'):  # 预审批通过 未核扣, 预核扣
                if I_E_Port == 'I':
                    YINUM += Decimal(str(obj.get("DclQty")))
                else:
                    YENUM += Decimal(str(obj.get("DclQty")))
            # todo 预审批下来爬取的状态第一次是预核扣以及未核扣, 然后第二次是预审批通过, 已核扣
            elif self.msg_data.get("DecState") == 'CR_4' and (VrfdedMarkcd == '2'):  # 预审批通过 已核扣
                if I_E_Port == 'I':  # 进口
                    ZINUM += Decimal(str(obj.get("DclQty")))
                    YINUM -= Decimal(str(obj.get("DclQty")))
                elif I_E_Port == 'E':  # 出口
                    ZENUM += Decimal(str(obj.get("DclQty")))
                    YENUM -= Decimal(str(obj.get("DclQty")))
            # todo 海关终审批通过 未核扣
            elif self.msg_data.get("DecState") == 'CR_9' and VrfdedMarkcd == '1':
                if I_E_Port == 'I':  # 进口
                    pass
                elif I_E_Port == 'E':  # 出口
                    YENUM += Decimal(str(obj.get("DclQty")))
            else:
                pass
            data['ZINUM'] = ZINUM
            data['ZENUM'] = ZENUM
            data['YINUM'] = YINUM
            data['YENUM'] = YENUM
            self.sql_operation(inventory, obj, data)


class InventoryNemsDataCreate(object):
    def __init__(self, item):
        self.item = item
        self.msg_s = item.get("msg_data")
        self.head_s = item.get('head_data')
        self.list_s = item.get('list_data')
        self.get_sql_data()

    def get_sql_data(self):
        self.sql = Sql(settings.DATABASES)

        # 这里针对不同的情况进行判断，对库存进行操作
        if self.msg_s.get('DecState') == 'CR_9' and self.head_s['VrfdedMarkcd'] == '2':  # 终审批通过,
            self.first_final_data()
        elif self.msg_s.get('DecState') == 'CR_4' and self.head_s['VrfdedMarkcd'] == '2':  # 预审批通过, 已核扣
            self.trial_batch_finally()
        elif self.msg_s.get('DecState') == 'CR_4' and (
                self.head_s['VrfdedMarkcd'] == '0' or self.head_s['VrfdedMarkcd'] == '1'):  # 预审批通过, 未核扣，预核扣
            self.trial_batch_begin()
        elif (self.msg_s.get('DecState') == 'CR_9' and self.head_s[
            'VrfdedMarkcd'] == '2'):  # 爬取的是总审批通过，已核扣， 更新之前的是 预审批通过，未核扣，预核扣 或者 爬取的预审批通过，已核扣
            # todo 这里需要重新组合数据
            self.double_state_chage()
        elif (self.msg_s.get('DecState') == 'CR_9' and
              self.head_s['VrfdedMarkcd'] == '2'):  # # 爬取的是总审批通过，已核扣, 数据库是 预审批通过，已核扣
            pass  # 不做任何操作
            logger.error(
            "爬取的是总审批通过，已核扣, 数据库是 预审批通过，已核扣{},{}".format(self.msg_s.get('DecState'), self.head_s['VrfdedMarkcd'],
                                                              ))

        elif self.msg_s.get('DecState') == 'CR_9' and self.head_s['VrfdedMarkcd'] == '1':  # 爬起是终审批通过，未核扣
            self.last_undeductible()
        elif self.msg_s.get('DecState') == 'CR_9' and self.head_s['VrfdedMarkcd'] == '2':  # 终审批通过，已核扣  -- 终审批通过 未核扣
            self.trial_batch_finally_join()
        else:
            logger.error("走的其他条件逻辑{},{}".format(self.msg_s.get('DecState'), self.head_s['VrfdedMarkcd'],
                                                ))

    def double_state_chage(self):
        """
        author: allen
        date: 19/7/26
        description: 海关总审批通过，未核扣
        :return:
        """
        for obj in self.list_s:
            data = {}
            inventory, YINUM, YENUM, ZINUM, ZENUM = self.data_clear_all(obj)
            if self.head_s.get("ImpexpMarkcd") == 'I':  # 进口
                ZINUM += Decimal(str(obj.get("DclQty")))
                YINUM -= Decimal(str(obj.get("DclQty")))
                if YINUM < 0:
                    logger.error("YINUM = {}, 这里不应该是负数".format(YINUM))
            elif self.head_s.get("ImpexpMarkcd") == 'E':  # 出口
                ZENUM += Decimal(str(obj.get("DclQty")))
                YENUM -= Decimal(str(obj.get("DclQty")))
                if YENUM < 0:
                    logger.error("YENUM = {}, 这里不应该是负数".format(YINUM))

            data['ZINUM'] = ZINUM
            data['ZENUM'] = ZENUM
            data['YINUM'] = YINUM
            data['YENUM'] = YENUM
            self.sql_operation(inventory, obj, data)

    def last_undeductible(self):
        """
                author: allen
                date: 19/7/26
                description: 海关总审批通过，未核扣
                :return:
                """
        for obj in self.list_s:
            data = {}
            inventory, YINUM, YENUM, ZINUM, ZENUM = self.data_clear_all(obj)
            if self.head_s.get("ImpexpMarkcd") == 'I':  # 进口
                pass
            elif self.head_s.get("ImpexpMarkcd") == 'E':  # 出口
                YENUM += Decimal(str(obj.get("DclQty")))

            data['ZINUM'] = ZINUM
            data['ZENUM'] = ZENUM
            data['YINUM'] = YINUM
            data['YENUM'] = YENUM
            self.sql_operation(inventory, obj, data)

    def data_clear_all(self, obj):
        """
            author: allen
            date: 19/7/22
            description: 对数据进行初始化
        """
        inventory = self.sql.select("NewsInvtStatistics", where={"GNO": obj.get('PutrecSeqno')}, first=True)
        YINUM = Decimal(str(inventory.get('YINUM'))) if inventory else 0  # 预增数量: 核注清单数据状态为预审批通过的进口保税核注清单备案序号申报数量
        YENUM = Decimal(str(inventory.get('YENUM'))) if inventory else 0  # 预扣数量：核注清单数据状态为预审批通过的出口保税核注清单备案序号申报数量
        ZINUM = Decimal(str(inventory.get('ZINUM'))) if inventory else 0  # 实增数量：核注清单数据状态为海关终审通过的进口保税核注清单备案序号申报数量
        ZENUM = Decimal(str(inventory.get('ZENUM'))) if inventory else 0  # 实扣数量：核注清单数据状态为海关终审通过的出口保税核注清单备案序号申报数量

        return inventory, YINUM, YENUM, ZINUM, ZENUM

    def sql_operation(self, inventory, obj, data):
        """
        author: allen
        date: 19/7/22
        description: 对数据存放在数据库中
        :param inventory:
        :param obj:
        :return:
        """
        INVENTORYNUM = Decimal(str(data['ZINUM'])) + Decimal(str(data['YINUM'])) - Decimal(str(data['ZENUM'])) - Decimal(str(data['YENUM']))  # 库存数量: 实增数量+预增数量-实扣数量-预扣数量
        DECLARENUM = Decimal(str(data['ZINUM']))- Decimal(str(data['ZENUM'])) - Decimal(str(data['YINUM']))  # 可申报数量: 实增数量-实扣数量-预扣数量
        # todo 这里需要和义新的进行组合，组合完成后一起入库表体的表
        datas = self.sql.select("Commodity", "monitoring_condition", "quarantine_category",
                                where={"codets": obj.get('Gdecd')},
                                first=True)
        self.MonitoringCondition = datas.get("monitoring_condition")
        self.QuarantinCategory = datas.get("quarantine_category")
        obj["YINUM"] = data.get('YINUM')
        obj["YENUM"] = data.get('YENUM')
        obj["ZINUM"] = data.get('ZINUM')
        obj["ZENUM"] = data.get('ZENUM')
        obj["INVENTORYNUM"] = INVENTORYNUM
        obj["DECLARENUM"] = DECLARENUM
        obj['MonitoringCondition'] = self.MonitoringCondition
        obj['QuarantinCategory'] = self.QuarantinCategory


        if inventory:
            print("进来了sssss")
            if obj.get('PutrecSeqno'):
                self.update_data(data, INVENTORYNUM, DECLARENUM, obj, obj.get('PutrecSeqno'))
            else:
                self.update_data(data, INVENTORYNUM, DECLARENUM, obj, obj.get('Param3'))
            # self.sql.update("NewsInvtStatistics", **{
            #     "YINUM": Decimal(str(data['YINUM']),
            #     "YENUM": Decimal(str(data['YENUM']),
            #     "ZINUM": Decimal(str(data['ZINUM']),
            #     "ZENUM": Decimal(str(data['ZENUM']),
            #     "INVENTORYNUM": Decimal(str(INVENTORYNUM),
            #     "DECLARENUM": Decimal(str(DECLARENUM),
            #     "MonitoringCondition": obj.get("MonitoringCondition"),
            #     "QuarantinCategory": obj.get("QuarantinCategory")
            # }, where={"GNO": obj.get('PutrecSeqno')})
            # logger.info("备案序号数据更新成功{}".format(obj.get('PutrecSeqno')))
        else:
            if obj.get("PutrecSeqno"):
                self.insert_data(data, INVENTORYNUM, DECLARENUM, obj, obj.get('PutrecSeqno'))
            else:
                self.insert_data(data, INVENTORYNUM, DECLARENUM, obj, obj.get("Param3"))
            # self.sql.insert("NewsInvtStatistics", **{
            #     "GNO": obj.get('PutrecSeqno'),
            #     "YINUM": Decimal(str(data['YINUM']),
            #     "YENUM": Decimal(str(data['YENUM']),
            #     "ZINUM": Decimal(str(data['ZINUM']),
            #     "ZENUM": Decimal(str(data['ZENUM']),
            #     "INVENTORYNUM": Decimal(str(INVENTORYNUM),
            #     "DECLARENUM": Decimal(str(DECLARENUM),
            #     "MonitoringCondition": obj.get("MonitoringCondition"),
            #     "QuarantinCategory": obj.get("QuarantinCategory")
            # }, )
            # logger.info("备案序号数据添加成功{}".format(obj.get('PutrecSeqno')))

    def update_data(self, data, INVENTORYNUM, DECLARENUM, obj, category):
        self.sql.update("NewsInvtStatistics", **{
            "YINUM": Decimal(str(data['YINUM'])),
            "YENUM": Decimal(str(data['YENUM'])),
            "ZINUM": Decimal(str(data['ZINUM'])),
            "ZENUM": Decimal(str(data['ZENUM'])),
            "INVENTORYNUM": Decimal(str(INVENTORYNUM)),
            "DECLARENUM": Decimal(str(DECLARENUM)),
            "MONITORING": self.MonitoringCondition,
            "QUARANTINE": self.QuarantinCategory
        }, where={"GNO": category})
        logger.info("备案序号数据更新成功{}".format(category))

    def insert_data(self, data, INVENTORYNUM, DECLARENUM, obj, category):
        self.sql.insert("NewsInvtStatistics", **{
            "GNO": category,
            "YINUM": Decimal(str(data['YINUM'])),
            "YENUM": Decimal(str(data['YENUM'])),
            "ZINUM": Decimal(str(data['ZINUM'])),
            "ZENUM": Decimal(str(data['ZENUM'])),
            "INVENTORYNUM": Decimal(str(INVENTORYNUM)),
            "DECLARENUM": Decimal(str(DECLARENUM)),
            "MONITORING": self.MonitoringCondition,
            "QUARANTINE": self.QuarantinCategory
        }, )
        logger.info("备案序号数据添加成功{}".format(category))

    def first_final_data(self):
        """
         author: allen
         date: 19/7/22
         description: 爬去数据直接是海关终审批通过
        :return:
        """

        for obj in self.list_s:
            data = {}
            inventory, YINUM, YENUM, ZINUM, ZENUM = self.data_clear_all(obj)
            # todo 直接是终审批通过, 不经过预审批操作
            if self.msg_s.get("DecState") == 'CR_9' and self.head_s['VrfdedMarkcd'] == '2':  # 终审批通过
                if self.head_s.get("ImpexpMarkcd") == 'I':  # 进口
                    ZINUM += Decimal(str(obj.get("DclQty")))
                    data['ZINUM'] = ZINUM
                    if ZINUM < 0:
                        logger.error("YINUM = {}, 这里不应该是负数".format(ZINUM))
                elif self.head_s.get("ImpexpMarkcd") == 'E':  # 出口k
                    ZENUM += Decimal(str(obj.get("DclQty")))
                    data['ZENUM'] = ZENUM
                    if ZENUM < 0:
                        logger.error("YENUM = {}, 这里不应该是负数".format(ZENUM))
                data['YINUM'] = YINUM
                data['YENUM'] = YENUM
                data['ZINUM'] = ZINUM
                data['ZENUM'] = ZENUM
                self.sql_operation(inventory, obj, data)

    def trial_batch_finally(self):
        """
         author: allen
         date: 19/7/22
         description: 爬去数据直接是预审批通过, 已核扣
        :return:
        """
        VrfdedMarkcd = self.head_s.get("VrfdedMarkcd")  # 核扣标记代码 0未核扣,1预核扣,2已核扣
        I_E_Port = self.head_s.get("ImpexpMarkcd")  # 进出口标志
        for obj in self.list_s:
            data = {}
            inventory, YINUM, YENUM, ZINUM, ZENUM = self.data_clear_all(obj)
            # todo 爬去数据直接是预审批通过, 已核扣
            if I_E_Port == 'I':  # 进口
                ZINUM += Decimal(str(obj.get("DclQty")))
            elif I_E_Port == 'E':  # 出口
                ZENUM += Decimal(str(obj.get("DclQty")))
            data['ZINUM'] = ZINUM
            data['ZENUM'] = ZENUM
            data['YINUM'] = YINUM
            data['YENUM'] = YENUM
            self.sql_operation(inventory, obj, data)

    def trial_batch_begin(self):
        """
         author: allen
         date: 19/7/22
         description: 爬去数据直接是预审批通过, 未核扣, 预核扣
        :return:
        """
        VrfdedMarkcd = self.head_s.get("VrfdedMarkcd")  # 核扣标记代码 0未核扣,1预核扣,2已核扣
        I_E_Port = self.head_s.get("ImpexpMarkcd")  # 进出口标志
        for obj in self.list_s:
            data = {}
            inventory, YINUM, YENUM, ZINUM, ZENUM = self.data_clear_all(obj)
            # todo 爬去数据直接是预审批通过, 未核扣, 预核扣
            if I_E_Port == 'I':  # 进口
                YINUM += Decimal(str(obj.get("DclQty")))
            elif I_E_Port == 'E':  # 出口
                YENUM += Decimal(str(obj.get("DclQty")))
            data['ZINUM'] = ZINUM
            data['ZENUM'] = ZENUM
            data['YINUM'] = YINUM
            data['YENUM'] = YENUM
            self.sql_operation(inventory, obj, data)

    def trial_batch_finally_join(self):
        """
         author: allen
         date: 19/7/22
         description: 爬去数据终审批通过, 未核扣-----终审批通过, 已核扣
        :return:
        """
        VrfdedMarkcd = self.head_s.get("VrfdedMarkcd")  # 核扣标记代码 0未核扣,1预核扣,2已核扣
        I_E_Port = self.head_s.get("ImpexpMarkcd")  # 进出口标志
        for obj in self.list_s:
            data = {}
            inventory, YINUM, YENUM, ZINUM, ZENUM = self.data_clear_all(obj)
            # todo 爬去数据终审批通过, 未核扣-----终审批通过, 已核扣
            if I_E_Port == 'I':  # 进口
                ZINUM += Decimal(str(obj.get("DclQty")))
            elif I_E_Port == 'E':  # 出口
                ZENUM += Decimal(str(obj.get("DclQty")))
                YENUM += Decimal(str(obj.get("DclQty")))
            data['ZINUM'] = ZINUM
            data['ZENUM'] = ZENUM
            data['YINUM'] = YINUM
            data['YENUM'] = YENUM
            self.sql_operation(inventory, obj, data)
