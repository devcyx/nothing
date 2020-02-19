# -*- coding: utf-8 -*-

# Scrapy settings for NemsSpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'NemsSpider'

SPIDER_MODULES = ['NemsSpider.spiders']
NEWSPIDER_MODULE = 'NemsSpider.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 1

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.1
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'NemsSpider.middlewares.NemsspiderSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   'NemsSpider.middlewares.NemsspiderDownloaderMiddleware': 543,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'NemsSpider.pipelines.NemsspiderMyMongoPipeline': 200,
   'NemsSpider.pipelines.NemsspiderMysqlPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

#百度api设置
APP_ID = '11637191'
API_KEY = 'EWGorLT3vvsXzqDaYDomFfgZ'
SECRET_KEY = 'zzAmHT8WAtutsoMfjYsL4jfFON9P0y3z'
# redis设置
HOST = "111.230.151.179"
PORT = 6379
DB = 10
PASSWORD = "!@admin"

# mongo设置
MONGO_HOST = "172.18.2.193"
MONGO_PORT = 27017

# 机保
NEMS_USERNAME = 'libin888'
NEMS_PASSWD = 'd5cda7c39bb8123ce1cb56d266aac911'
# 前海
DEC_USERNAME = 'HULIXIA'
DEC_PASSWD = 'ad5607bd2a5bdf30a73b3f1cfe9725ce'
# 东莞
DW_USERNAME = "DGBT010"
DW_PASSWD = "03b157c6c1e2b7f5c53d260a8ec8d0da"

import os

PROJECT_log = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# log相关配置
# LOG_LEVEL = "INFO"
LOG_BASE_DIR = os.path.join(PROJECT_log, "logs\\task.log")
LOG_WHEN = "D"  # when 是一个字符串,M: Minutes;H: Hours;D: Days
LOG_INTERVAL = 1  # 是指等待多少个单位when的时间后，Logger会自动重建文件
LOG_BACKUPCOUNT = 0  # 是保留日志个数。默认的0是不会自动删除掉日志。


RE_CONNECT_SQL_TIME = 10    # 数据库重连次数
RE_CONNECT_SQL_WAIT_TIME = 5    # 重连数据库等待时间，s
# DATABASES = {
#    'host': '111.230.242.51',
#    'port': 3306,
#    'user': 'btrProject',
#    'password': 'welcome2btr',
#    'db': 'goldtwo8.1',
#    'charset': 'utf8',
# }

DATABASES = {
   'host': 'gz-cdb-ld4ka6l5.sql.tencentcdb.com',
   'port': 63482,
   'user': 'gmb_bt',
   'password': 'glodtwo!@456',
   'db': 'GMBGTEO',
   'charset': 'utf8',
}
DW_DATABASES = {
   'host': 'gz-cdb-ld4ka6l5.sql.tencentcdb.com',
   'port': 63482,
   'user': 'gmb_bt',
   'password': 'glodtwo!@456',
   'db': 'GMBGTEODW',
   'charset': 'utf8',
}

