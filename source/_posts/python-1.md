---
title: PYTHON笔记1 从BING网站下载图片
date: 2018-05-28 20:09:03
tags: [python]
categories: python
---

从BING网站下载图片，方便博客中使用  
转载(https://blog.csdn.net/csnd_ayo/article/details/73691549)

又发现一段代码更合适的代码
转载(https://www.cnblogs.com/pillarcao/p/9085314.html)

![示例图片](python-1/3037187.jpg)

<!--more-->

## 示例代码

```
# -*- coding:utf-8 -*-

import urllib.request
import datetime


# @brief  打开网页
# url : 网页地址
# @return 返回网页数据
def open_url(url):
    # 根据当前URL创建请求包
    req = urllib.request.Request(url)
    # 添加头信息，伪装成浏览器访问
    req.add_header('User-Agent',
                   'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36')
    # 发起请求
    response = urllib.request.urlopen(req)
    # 返回请求到的HTML信息
    return response.read()


# 找图片
def find_picture_url(http_response):
    # 查找当前页面所有图片的URL
    http_response = http_response.decode('utf-8')
    img_addrs = []
    # 找图片
    a = http_response.find('<url>')
    # 不带停，如果没找到则退出循环
    while a != -1:
        # 以a的位置为起点，找以jpg结尾的图片
        b = http_response.find('</url>', a, a+255)
        # 如果找到就添加到图片列表中
        if b != -1:
            img_addrs.append(http_response[a+5:b])
        # 否则偏移下标
        else:
            b = a + 5
        # 继续找
        a = http_response.find('<url>', b)

    return img_addrs

# url 拼接


def url_joint(picture_url):
    return "http://cn.bing.com/" + picture_url


# @brief 保存图片
# url : 图片url
# addr  : 保存的地址
def save_picture(url, addr):
    with open(addr, 'wb') as f:
        img = open_url(url_joint(url))
        if img:
            f.write(img)
    print("图片已保存")
    return


i = 0
while i < 5:
    i += 1
    # [1] 打开网页
    temp_str = "http://cn.bing.com/HPImageArchive.aspx?format=xml&idx=%d&n=100" % (
        i)

    response = open_url(temp_str)
    # [2] 找到图片
    list_picture = find_picture_url(response)
    local_time = datetime.datetime.now().microsecond
    j = 0

    # [3] 保存图片
    for picture_url in list_picture:
        j += 1
        local_time_file_name = str(local_time) + str(j) + ".jpg"
        print(local_time_file_name)
        save_picture(picture_url, local_time_file_name)

```

## 示例代码2
参考(https://www.cnblogs.com/pillarcao/p/9085314.html)
```
# 下载网络图片设置壁纸
# 2018/5/21 clz
# win10 ,python3.0

import requests
from bs4 import BeautifulSoup
import os
import datetime
import PIL.Image
import win32api
import win32con
import win32gui
import re

os.makedirs('Bing', exist_ok=True)
dt = datetime.datetime.now()
dtAsFileNmae = str(dt.year) + '0' + str(dt.month) + str(dt.day)
img_path = os.path.abspath(os.path.join('Bing', dtAsFileNmae+'.jpg'))

print(img_path)


def set_wallpaper_from_bmp(bmp_path):
    # 打开指定注册表路径
    reg_key = win32api.RegOpenKeyEx(
        win32con.HKEY_CURRENT_USER, "Control Panel\\Desktop", 0, win32con.KEY_SET_VALUE)
    # 最后的参数:2拉伸,0居中,6适应,10填充,0平铺
    win32api.RegSetValueEx(reg_key, "WallpaperStyle", 0, win32con.REG_SZ, "2")
    win32api.RegSetValueEx(reg_key, "TileWallpaper", 0, win32con.REG_SZ, "0")
    # 刷新桌面
    win32gui.SystemParametersInfo(
        win32con.SPI_SETDESKWALLPAPER, bmp_path, win32con.SPIF_SENDWININICHANGE)


def set_wallpaper(bmp_path):
    img_dir = os.path.dirname(bmp_path)
    bmpImg = PIL.Image.open(bmp_path)
    new_bmp_path = os.path.join(img_dir, 'wallpaper.bmp')
    bmpImg.save(new_bmp_path, "BMP")
    set_wallpaper_from_bmp(new_bmp_path)


def getTopPictureFromBingWallpaper():
    # 从Bing当日美图下载第一幅图片
    url = 'http://bingwallpaper.com/cn'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    imageLst = soup.select('.cursor_zoom img')
    image_url = imageLst[0].get('src')
    res = requests.get(image_url)
    with open(img_path, 'wb') as file:
        file.write(res.content)


if __name__ == '__main__':
    getTopPictureFromBingWallpaper()
    # set_wallpaper(img_path)
a = input('please input any key to continue!')

```
