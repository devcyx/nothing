import redis

from NemsSpider import settings


class RedisApp(object):
    """redis封装"""
    def __init__(self):
        self.r = redis.Redis(host=settings.HOST, port=settings.PORT, decode_responses=True, db=settings.DB,
                             password=settings.PASSWORD)
        # self.pipe = self.r.pipeline(transaction=True)

    def get_warning_keys(self):
        """获取warning所有的keys"""
        return self.r.keys('warning')

    def get_keys(self, key='*'):
        """获取key，默认获取所有的key"""
        return self.r.keys(key)

    def get_hkeys(self, hname):
        """获取字典所有的key"""
        return self.r.hkeys(hname)

    def get_hvals(self, hname):
        """获取字典所有的val"""
        return self.r.hkeys(hname)

    def get_hall(self, hname):
        """获取整个字典"""
        return self.r.hgetall(hname)

    def get_warning_hall(self):
        """获取warning整个字典"""
        return self.r.hgetall('warning')

    def get_overdue_hall(self):
        """获取overdue整个字典"""
        return self.r.hgetall('overdue')

    def get_warning_count(self):
        """获取warning的count"""
        return self.r.hlen('warning')

    def get_overdue_count(self):
        """获取overdue的count"""
        return self.r.hlen('overdue')

    def get_warning_and_overdue_count(self):
        """获取warning和overdue的count"""
        return self.r.hlen('warning'), self.r.hlen('overdue')

    def get_count(self, key):
        """获取字典对应的count"""
        return self.r.hlen(key)

    def get_hget(self, key, hname):
        """获取字典对应kes的val"""
        return self.r.hget(key, hname)

    def get_warning_hget(self, hname):
        """获取warning字典key的val"""
        return self.r.hget('warning', hname)

    def get_overdue_hget(self, hname):
        """获取overdue字典key的val"""
        return self.r.hget('overdue', hname)

    def del_hkeys(self, hname, key):
        """删除字典对应的key"""
        return self.r.hdel(hname, key)

    def del_warning_hkeys(self, key):
        """删除warning字典对应的key"""
        return self.r.hdel('warning', key)

    def del_overdue_hkeys(self, key):
        """删除overdue字典对应的key"""
        return self.r.hdel('overdue', key)

    def del_keys(self, key):
        """删除key"""
        return self.r.delete(key)

    def set_hset(self, key, hname, hval):
        """设置字典key对应val"""
        return self.r.hset(key, hname, hval)

    def set_warning_hset(self, hname, hval):
        """设置warning字典key对应val"""
        return self.r.hset('warning', hname, hval)

    def set_overdue_hset(self, hname, hval):
        """设置overdue字典key对应val"""
        return self.r.hset('overdue', hname, hval)

    def get_redis_instance(self):
        """获取redis实例"""
        return self.r


if __name__ == "__main__":
    print(RedisApp().get_warning_and_overdue_count())
    print(RedisApp().del_keys('overdue'))
    print(RedisApp().del_keys('warning'))
    print(RedisApp().get_keys())

