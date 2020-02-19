"""
Description:
Author: song bo
Action      Date        Content
------------------------------------
Create      2019-
"""
import hashlib
import json
import re

from lxml import etree
import requests
from aip import AipOcr

from NemsSpider import settings
from NemsSpider.utils.redis_app import RedisApp

from NemsSpider.utils.log import getlogger

log = getlogger(__name__)


class Login(object):
    login_url = "http://app.singlewindow.cn/cas/login"
    image_url = "http://app.singlewindow.cn/cas/plat_cas_verifycode_gen?r=0.41473693848207716"
    ImageDir = './'
    image_cookie = ""
    aipOcr = AipOcr(settings.APP_ID, settings.API_KEY, settings.SECRET_KEY)
    cookie_url = "http://sz.singlewindow.cn/dyck/swProxy/deskserver/sw/deskIndex?menu_id=sas"

    header = {
        'Host': 'app.singlewindow.cn',
        'Origin': 'http://app.singlewindow.cn',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
    }
    flag = False
    pyredis = RedisApp().get_redis_instance()
    session = requests.Session()

    def __init__(self, sources):
        """
        :description 初始化
        :author song bo
        :param sources: dec or nems
        """
        self.sources = sources
        self.USERNAME = settings.DEC_USERNAME if sources == "dec" else settings.NEMS_USERNAME
        self.PASSWD = settings.DEC_PASSWD if sources == "dec" else settings.NEMS_PASSWD
        self.COOKIES_NAME = "request_cookies" if sources == "nems" else "dec_request_cookies"
        self.cookies_key_list = ['!Proxy!JSESSIONID', '!Proxy!route1plat', 'JSESSIONID']

    def start_requests(self):
        while not self.flag:
            response = self.session.get(self.login_url, headers=self.header)
            self.image_cookie = self.parse_cooike()
            content = etree.HTML(response.text)
            self.login1(content)

    def login1(self, response):
        """
        :description 获取cookies
        :author song bo
        :param response:
        :return:
        """
        def know_Image():
            """
            :description 图片验证
            :author song bo
            :return:
            """
            code_count = 0
            while code_count < 20:
                code_count += 1
                content = self.session.get(self.image_url, cookies=self.image_cookie, headers=self.header)
                value = self.aipOcr.basicGeneral(content.content)
                try:
                    value = re.sub(r'[^a-zA-Z0-9]', '', value['words_result'][0]['words'])
                except:
                    continue
                if 4 == len(value) and re.match('^[0-9a-zA-Z]{4}$', value):
                    with open('../../images.jpg', 'wb') as f:
                        f.write(content.content)
                    return value

        lt = response.xpath(r'//*[@id="fm1"]/p[1]/input[1]/@value')[0]
        execution = response.xpath(r'//*[@id="fm1"]/p[1]/input[2]/@value')[0]
        data = {
            'swy': self.USERNAME,
            'swm': self.PASSWD,
            'swm2': '',
            'verifyCode': know_Image(),
            'lt': lt,
            '_eventId': 'submit',
            'execution': execution,
            'swLoginFlag': 'swUp',
            'lpid': 'P1',
            'name': ''
        }
        header = {
            'Host': 'app.singlewindow.cn',
            'Origin': 'http://app.singlewindow.cn',
            'Referer': 'http://app.singlewindow.cn/cas/login?_local_login_flag=1&service=http://app.singlewindow.cn/cas/jump.jsp%3FtoUrl%3DaHR0cDovL2FwcC5zaW5nbGV3aW5kb3cuY24vY2FzL29hdXRoMi4wL2F1dGhvcml6ZT9jbGllbnRfaWQ9MTM2NyZyZXNwb25zZV90eXBlPWNvZGUmcmVkaXJlY3RfdXJpPWh0dHAlM0ElMkYlMkZzei5zaW5nbGV3aW5kb3cuY24lMkZkeWNrJTJGT0F1dGhMb2dpbkNvbnRyb2xsZXI=&localServerUrl=http://sz.singlewindow.cn/dyck&localDeliverParaUrl=/deliver_para.jsp&colorA1=d1e4fb&colorA2=66,%20124,%20193,%200.8',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Upgrade-Insecure-Requests': '1',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',
        }
        content = self.session.post(self.login_url, data=data, headers=header, cookies=self.image_cookie, timeout=30)
        self.parse_login(content)

    def parse_login(self, response):
        if response.text.find("登录成功") > 0:
            print('模拟登陆成功！！！')
            # 到这里我们的登录状态已经写入到response header中的'Set-Cookies'中了,
            headers = {
                'Accept': 'application/json, text/javascript, */*; q=0.01',
                'X-Requested-With': 'XMLHttpRequest',
                'Content-Type': 'application/json',
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.181 Safari/537.36',

            }
            self.session.headers.update(headers)
            self.session.get(self.cookie_url, verify=False)
            # 提取response中的cookie
            all_cookies = self.parse_cooike()
            cookies = {key: all_cookies.get(key) for key in self.cookies_key_list}
            self.pyredis.set(self.COOKIES_NAME, json.dumps(cookies))
            self.flag = True
        elif response.text.find("验证码错误请重新输入") > 0:
            print("验证码错误请重新输入")
        else:
            print("模拟登陆失败！！")

    def parse_cooike(self):
        cookie_jar = self.session.cookies.get_dict()
        return cookie_jar


class DWLogin(Login):
    cookie_url = "http://www.singlewindow.gd.cn/swProxy/deskserver/sw/deskIndex?menu_id=sas"

    def __init__(self):
        """
        :description 初始化
        :author song bo
        :param sources: dec or nems
        """
        # self.sources = sources
        self.USERNAME = settings.DW_USERNAME
        self.PASSWD = settings.DW_PASSWD
        self.COOKIES_NAME = "dw_request_cookies"
        self.cookies_key_list = ['!Proxy!JSESSIONID', '!Proxy!route1plat', 'JSESSIONID', 'SERVERID']


if __name__ == '__main__':
    # a = Login("dec")
    a = DWLogin()
    a.start_requests()
