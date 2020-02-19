"""
Description:
Author: Alvin yx
Action      Date        Content
------------------------------------
Create      2019-
"""
import time

from selenium import webdriver
browser = webdriver.Chrome(r"E:\other\pyselenium\driver\chromedriver.exe")


def login():
    # 打开淘宝登录页，并进行扫码登录
    browser.get("https://www.taobao.com")
    # time.sleep(3)
    if browser.find_element_by_link_text("亲，请登录"):
        browser.find_element_by_link_text("亲，请登录").click()
        print("请在30秒内扫码验证！")
        time.sleep(30)


def colse():
    browser.quit()


# 打开购物车
def open_car():
    browser.find_element_by_id("mc-menu-hd").click()
    pass


def run():
    login()
    open_car()
    colse()


if __name__ == '__main__':
    run()
