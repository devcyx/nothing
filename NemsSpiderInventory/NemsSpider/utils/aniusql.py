import time
import traceback

import pymysql
import re

from DBUtils.PooledDB import PooledDB

from NemsSpider import settings
from .log import getlogger

log = getlogger(__name__)


class SqlResultObj(object):
    def __init__(self):
        self.status = False
        self.id = None
        self.result = None

    def __str__(self):
        if self.status:
            return '操作成功'
        return '操作失败'


class Sql(object):
    def __init__(self, databases):
        self.databases = databases
        self.conn = None
        self.cursor = None
        self._connect_mysql()
        self.auto_commit = True

    def __new__(cls, databases, *args, **kwargs):
        if not hasattr(cls, '_instance'):
            setattr(cls, '_instance', super(Sql, cls).__new__(cls, *args, **kwargs))
        return getattr(cls, '_instance')

    def commit_if_auto_commit(self):
        if self.auto_commit:
            self.conn.commit()

    def _connect_mysql(self):
        """创建数据库连接池"""
        times = settings.RE_CONNECT_SQL_TIME
        while times > 0:
            d = {
                'mincached': 5,  # 初始化时，链接池中至少创建的空闲的链接，0表示不创建
                'maxcached': 5,  # 链接池中最多闲置的链接，0和None不限制
                'maxshared': 0,
            # 链接池中最多共享的链接数量，0和None表示全部共享。PS: 无用，因为pymysql和MySQLdb等模块的 threadsafety都为1，所有值无论设置为多少，_maxshared永远为0，所以永远是所有链接都共享。
                'maxconnections': 20,  # 连接池允许的最大连接数，0和None表示不限制连接数
                'blocking': True,  # 连接池中如果没有可用连接后，是否阻塞等待。True，等待；False，不等待然后报错
                'maxusage': None,  # 一个链接最多被重复使用的次数，None表示无限制
                'ping': 0,
            }
            try:
                _pool = PooledDB(pymysql, **d, **self.databases)
                self.conn = _pool.connection()
                self.cursor = self.conn.cursor()
                return True
            except:
                log.debug('创建连接池失败，暂停{}S后继续创建'.format(settings.RE_CONNECT_SQL_WAIT_TIME))
                print('创建连接池失败，暂停{}S后继续创建'.format(settings.RE_CONNECT_SQL_WAIT_TIME))
                times -= 1
                time.sleep(settings.RE_CONNECT_SQL_WAIT_TIME)

        log.error('数据库连接失败...')
        raise Exception('数据库连接失败...')

    def _reConn(self):
        try:
            self.conn.ping()  # cping 校验连接是否异常
        except:
            self._connect_mysql()

    def insert(self, table_name, **kwargs):
        self._reConn()
        keys, vals = tuple(kwargs.keys()), tuple(kwargs.values())
        cols = ",".join(keys)
        wildcards = ",".join(["%s" for i in range(len(vals))])
        ret = SqlResultObj()
        sql = 'insert into {}({}) VALUES ({});'.format(table_name, cols, wildcards)
        ret.status = self.cursor.execute(sql, args=vals)
        self.commit_if_auto_commit()
        ret.id = self.cursor.lastrowid
        return ret

    def update(self,table_name,where=None,no_where=False, **kwargs):
        """
        :param table_name:
        :param cols:
        :param where:
        :return:
        """
        self._reConn()
        if not no_where:
            assert where is not None, 'update 操作必须带where条件'
        filter_condition = ""  # 筛选条件
        vals_condition = tuple()
        if where:
            vals_condition = tuple(where.values())
            lens = len(where.items())
            for i, k in enumerate(where):
                if lens == 1:
                    filter_condition += "where {}=%s".format(k)
                else:
                    if i == 0:
                        filter_condition += "where {}=%s".format(k)
                    else:
                        filter_condition += " AND {}=%s".format(k)

        keys, vals = tuple(kwargs.keys()), tuple(kwargs.values())
        cols = ",".join(keys)
        wildcards = ",".join(["{}=%s".format(keys[i]) for i in range(len(vals))])

        sql = 'UPDATE {} SET {} {};'.format(table_name, wildcards, filter_condition)

        #将筛选条件的val加到tuple
        vals=vals+vals_condition
        ret = self.cursor.execute(sql, args=vals)   # 受影响的行
        self.commit_if_auto_commit()
        return ret

    def _select(self):
        pass

    def select(self, table_name, *cols, where=None, limit=None, first=False):
        """
        :param table_name: 表名,str
        :param cols: 列名
        :param where: 筛选条件,暂时只添加一个
        :param limit: 查询行数,int型,None表示查询苏所有
        SELECT * FROM DecMsg where ClientSeqNo="201801100950223990" and DeleteFlag="0"
        :return:
        """
        self._reConn()
        if limit:
            assert len(limit) == 2, 'limit 格式错误，格式类似[0, 10]'
        filter_condition = ""  # 筛选条件,暂时只支持一个查询条件
        vals=tuple()
        if where:
            vals=tuple(where.values())
            for i,k in enumerate(where):
                if len(vals)==1:
                    if k.endswith('__gt'):
                        filter_condition += 'where {}>%s'.format(k[:-4])
                    elif k.endswith('__lt'):
                        filter_condition += 'where {}<%s'.format(k[:-4])
                    else:
                        filter_condition += 'where {}=%s'.format(k)
                else:
                    if i==0:
                        if k.endswith('__gt'):
                            filter_condition += 'where {}>%s'.format(k[:-4])
                        elif k.endswith('__lt'):
                            filter_condition += 'where {}<%s'.format(k[:-4])
                        else:
                            filter_condition += 'where {}=%s'.format(k)
                    else:
                        if k.endswith('__gt'):
                            filter_condition += ' and {}>%s'.format(k[:-4])
                        elif k.endswith('__lt'):
                            filter_condition += ' and {}<%s'.format(k[:-4])
                        else:
                            filter_condition += ' and {}=%s'.format(k)

        if not cols and not limit:  # select * ,无limit
            sql = 'select * from {} {};'.format(table_name,filter_condition)
        elif limit:
            if not cols:  # select * 有limit
                sql = 'select * from {} {} limit {},{};'.format(table_name,filter_condition, limit[0], limit[1])
            else:  # select x1,x2 有limit
                col_names = ",".join(cols)
                sql = 'select {} from {} {} limit {},{};'.format(col_names, table_name,filter_condition, limit[0], limit[1])
        else:
            # no limit,有col值
            col_names = ",".join(cols)
            sql = 'select {} from {} {};'.format(col_names, table_name,filter_condition)

        self.cursor.execute(sql, vals)
        if self.cursor.description:
            names = [x[0] for x in self.cursor.description]

        self.conn.commit()
        if first:
            ret = self.cursor.fetchone()
            if ret:
                return dict(zip(names, ret))
            else:
                return None
        result = self.cursor.fetchall()
        rets = [x for x in result]
        ret_list = []
        for ret in rets:
            ret_list.append(dict(zip(names, ret)))
        return ret_list

    def all(self, table_name, *cols):
        self._reConn()
        col_names = ",".join(cols)
        sql = 'select {} from {};'.format(col_names, table_name)
        self.cursor.execute(sql)
        self.commit_if_auto_commit()
        return self.cursor.fetchall()

    def delete(self, table_name, where=None):
        self._reConn()
        filter_condition = "where "  # 筛选条件
        vals_condition = tuple()
        if where:
            vals_condition = tuple(where.values())
            for i, k in enumerate(where):
                results = re.match('^(.+?)__(.+?)$', k)
                if 1 == len(vals_condition):
                    if results:
                        if 'gt' == results.group(2):
                            filter_condition += "{}>%s".format(results.group(1))
                        elif 'lt' == results.group(2):
                            filter_condition += "{}<%s".format(results.group(1))
                    else:
                        filter_condition += "{}=%s".format(k)
                else:
                    if 0 == i:
                        if results:
                            if 'gt' == results.group(2):
                                filter_condition += "{}>%s".format(results.group(1))
                            elif 'lt' == results.group(2):
                                filter_condition += "{}<%s".format(results.group(1))
                        else:
                            filter_condition += "{}=%s".format(k)
                    else:
                        if results:
                            if 'gt' == results.group(2):
                                filter_condition += " and {}>%s".format(results.group(1))
                            elif 'lt' == results.group(2):
                                filter_condition += " and {}<%s".format(results.group(1))
                        else:
                            filter_condition += " and {}=%s".format(k)

        sql = 'DELETE FROM {} {};'.format(table_name, filter_condition)

        ret = self.cursor.execute(sql, args=vals_condition)
        self.commit_if_auto_commit()
        return ret

    def raw_sql(self, _sql, *args):
        """支持原生SQL"""
        self._reConn()
        ret = SqlResultObj()
        lines = self.cursor.execute(_sql, args)
        self.commit_if_auto_commit()
        if lines:
            ret.status = True
            if _sql.lower().startswith('select'):
                ret.result = self.cursor.fetchall()
        return ret


class DWSql(Sql):
    pass


class aniu_atomic(object):
    """适配当前文件Sql上下文管理事物"""
    def __init__(self, _sql):
        self.sql = _sql

    def __enter__(self):
        """with语句包裹起来的代码运行前执行，可写返回值，返回值会赋值给as后面的变量"""
        self.sql.auto_commit = False  # 关闭自动提交

    def __exit__(self, exc_type, exc_val, exc_tb):  # exc_type：异常类型  exc_val：异常名称  exc_tb：异常详细信息
        """当with包裹的语句块全部执行完毕后，自动调用此方法"""
        if exc_tb is None:  # 有异常信息会存在exc_tb中
            self.sql.conn.commit()  # 无异常提交
        else:
            self.sql.conn.rollback()  # 有异常回滚
        self.sql.auto_commit = True  # 事务执行完开启自动提交
        return False  # False:会抛出异常，中断程序的执行, True:不抛出异常


dw_sql = DWSql(settings.DW_DATABASES)
sql = Sql(settings.DATABASES)


if __name__ == "__main__":
    sql = Sql(settings.DATABASES_GOLD_8)
    sql1 = Sql(settings.DATABASES_GOLD_8)
    print(id(sql))
    print(id(sql1))
    # ret = sql.select('Msg', where={'id__gt': 85}, first=True)
    # ret.pop('id')
    # ret = sql.insert('Msg', **ret)
    # print("ret = ", ret)
