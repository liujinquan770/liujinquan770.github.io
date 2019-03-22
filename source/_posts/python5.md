---
title: PYTHON笔记5 定时检查并登陆公司上网授权网站
date: 2018-07-10 14:48:11
modified: 
tags: [python]
categories: python
---

公司上网环境受限，需要在授权网站登陆后才能正常上网。页面很简单，填写账号密码登陆即可，使用Fiddler4抓包后编写脚本实现自动检测和登陆。

![示例图片](python5/20180710.jpg)

<!--more-->

原理很简单，就是周期调用 ping命令检查是否能否上网，如果断网就使用requests访问授权网站填写账号密码登陆即可。

```python
#-*- encoding: utf-8 -*-
import requests
import time
import ConfigParser
import string
import os
import sys
import threading
import decimal

# url1 = 'http://192.168.0.2/login/servlet/PreLog;adt_myuid=0;jsessionid=?lan=1&username=test13&password=test13168&scheme=http&twice=1&authType=0'
# url2 = 'http://192.168.0.2/login/servlet/LoginServlet;adt_myuid=0;jsessionid=?lan=1&username=test13&password=test13168&url=http%3A%2F%2F192.168.0.2%2Flogin%2Findex_.jsp%3Badt_myuid%3D0%3Bjsessionid%3D%3ForginUrl%3Dhttp%3A%2F%2F192.168.0.2%2Flogin%2Findex.jsp&scheme=http&ifPl=undefined&authType=0&machCode=&ifRadomcode=undefined&radomcode=undefined'


# 读配置文件
def ReadConfig():
    print "reading config file..."
    cf = ConfigParser.ConfigParser()
    cf.read("config.ini")
    server = cf.get("account", "server")
    username = cf.get("account", "username")
    password = cf.get("account", "password")
    interval = cf.get("account", "interval")
    print "server={0},username={1},password={2},interval={3}".format(server, username, password, interval)
    return server, username, password, interval

#


def LoginServer(server, username, password):
    url1 = "http://{0}/login/servlet/PreLog;adt_myuid=0;jsessionid=?lan=1&username={1}&password={2}&scheme=http&twice=1&authType=0".format(
        server, username, password)
    url2 = "http://{0}/login/servlet/LoginServlet;adt_myuid=0;jsessionid=?lan=1&username={1}&password={2}&url=http%3A%2F%2F{0}%2Flogin%2Findex_.jsp%3Badt_myuid%3D0%3Bjsessionid%3D%3ForginUrl%3Dhttp%3A%2F%2F{0}%2Flogin%2Findex.jsp&scheme=http&ifPl=undefined&authType=0&machCode=&ifRadomcode=undefined&radomcode=undefined".format(
        server, username, password)
    headers = {'Connection': 'keep-alive',
               'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.221 Safari/537.36 SE 2.X MetaSr 1.0'}
    s = requests.Session()
    s.headers.update(headers)
    r = s.get(url1)
    print(r.text)
    time.sleep(0.1)
    r = s.get(url2)
    print(r.text)
    s.close()


def CheckOnline(interval):
    for i in range(1000000): #一百万分钟等于600多天
        print "ping to www.baidu.com"
        # 检查是否能上网
        try:
            # r = requests.get(url, timeout=1)
            # print r.status_code
            # if(r.status_code != 200):
            #     r.raise_for_status()    # 如果响应状态码不是 200，就主动抛出异常
            # requests不可靠,成功一次后总是返回200
            ret = os.system('ping www.baidu.com -n 1')  # 0成功，其他值失败
            if ret:
                print 'ping fail'
                server, username, password, _not_used = ReadConfig()
                LoginServer(server, username, password)
            else:
                print 'ping ok'
        except Exception as e:
            print(e)
            server, username, password, _not_used = ReadConfig()
            LoginServer(server, username, password)
        else:
            # result = r.text
            # print(result)
            pass
        time.sleep(interval)


def StartTimer():
    server, username, password, interval = ReadConfig()
    threads = []
    f_interval = float(interval)
    t1 = threading.Thread(target=CheckOnline, args=(f_interval,))
    threads.append(t1)
    for t in threads:
        t.setDaemon(True)
        t.start()
    t.join()
    print "all over"


if __name__ == "__main__":
    StartTimer()

```