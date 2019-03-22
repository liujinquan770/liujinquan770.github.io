---
title: PYTHON笔记2 从"纪录片天地"获取所有电影的百度网盘链接
date: 2018-05-31 16:52:39
tags: [python]
categories: python
---

这里以前写的下载纪录片的脚本

![示例图片](python2/8745071.jpg)

<!--more-->

# 目标

    最近想找一些纪录片电影来看，从知乎的文章中发现了纪录片天地([http://www.jlpcn.net](http://www.jlpcn.net/))这个网站。网站内的资源非常丰富，看过一些电影之后，有了批量下载电影的想法。

    查看网页的源代码后发现电影的链接，分类，描述等信息比较规则，适合使用脚本爬取。

# 实现思路
## 使用requests获取网页内容
```
def getSoup(self, url):
        '''使用request获取网页源代码,并传入bs'''
        headers = {
            'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
        }
        try:
            r = requests.get(url, headers=headers)
            r.encoding = 'utf-8'
            soup = bsp(r.text, "html.parser")
            return soup
        except Exception as identifier:
            print('getSoup ex:\n%s' % traceback.format_exc())
            return None
```
## 截取概要信息
以http://www.jlpcn.net/vodtypehtml/1.html页面为例，这是“内容分类”->“科普”类的第一页，总共23页。
![image.png](http://upload-images.jianshu.io/upload_images/10166460-2a9fc0d6c3b1068b.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
首先通过bs定位class='pages'的div元素，然后正则表达式提取总的页面数。
```
# 分析当前分类的纪录片有多少页
    def findAllLinks(self, url):
        '''
        纪录片分类的地址第一页
        http://www.jlpcn.net/vodtypehtml/1.html
        '''
        links = []
        links.append(url)
        soup = self.getSoup(url)
        if not soup:
            return None
        index1 = url.rfind('.')
        base1 = url[0:index1]
        div = soup.find('div', attrs={"class", "pages"})
        if div:
            pagestr = re.findall(r'当前:1/(.+?)页', div.text)
            if len(pagestr) > 0:
                try:
                    page_cnt = int(pagestr[0])
                    for x in range(2, page_cnt + 1):
                        url_t = "{0}-{1}.html".format(base1, x)
                        links.append(url_t)
                except Exception as ex:
                    traceback.print_exc()
        return links
```
提取页面总数后，然后可分析每一页总列举的电影的概要信息
![image.png](http://upload-images.jianshu.io/upload_images/10166460-f8fec60368063e6d.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

代码如下
```
# 在分类页面中查找当前页面的纪录片的概要信息
    def findMoives(self, url):
        resultList = []
        soup = self.getSoup(url)
        if not soup:
            return None
        # print(soup.encode_contents())
        li_list = soup.find_all('li', attrs={"class": "mov"})
        for li in li_list:
            imgbox = li.find('img', attrs={"class": "scrollLoading"})
            if imgbox:
                minfo = models.movie_summary()
                minfo.img_url = imgbox["data-url"]
                a_pic = li.find('a', attrs={"class": "pic"})
                if a_pic:
                    minfo.href = a_pic["href"]
                    minfo.title = a_pic["title"]
                    minfo.title = minfo.title.replace(' ', '')
                r1 = li.find('div', attrs={"class": "r1"})
                minfo.update_time = r1.string[5:]
                r3 = li.find_all('div', attrs={"class": "r3"})
                if r3 and len(r3) > 0:
                    for r in r3:
                        if "内容分类" in r.string:
                            minfo.content_category = r.string[5:]
                        elif "频道分类" in r.string:
                            minfo.channel_category = r.string[5:]
                        elif "语言字幕" in r.string:
                            minfo.subtitles = r.string[5:]
                        elif "最后更新" in r.string:
                            minfo.last_update_time = r.string[5:]
                r5 = li.find('div', attrs={"class": "r5"})
                minfo.last_update_time = r5.string[5:]
                print("http://www.jlpcn.net" + minfo.href, minfo.title)
                resultList.append(minfo)
        print(len(li_list))
        return resultList
```
## 进入下一层页面，获取更详细信息
以http://www.jlpcn.net/vodhtml/3308.html为例，进入页面后
![image.png](http://upload-images.jianshu.io/upload_images/10166460-1dfa7de00d06ac94.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
图中标注的位置的几个按钮，对应的超链接就是纪录片的百度网盘地址。分析网页源代码，定位到这些超链接的位置。
![image.png](http://upload-images.jianshu.io/upload_images/10166460-52020cf186e1541b.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)
代码如下，
```
# 获取纪录片的详细信息
    def findMovieDetail(self, url):
        resultList = []
        soup = self.getSoup(url)
        if not soup:
            return None

        down_list_2 = soup.find('div', attrs={"id", "down_list_2"})
        if down_list_2:
            scripts = down_list_2.find_all('script')
            if len(scripts) > 0:
                for script in scripts:
                    print(script.string)

        div_list = soup.find_all('div', attrs={"class": "wanpan"})
        for div in div_list:
            a_bd = div.find('a')
            href = a_bd["href"]
            text = a_bd.string
            if not text:
                text = ','.join(a_bd.strings)
            text = text.replace(' ', '')
            # print(href, text)
            detail = models.movie_detail()
            detail.cur_url = url
            detail.title = text
            detail.href = href

            resultList.append(detail)
        # last_url = resultList[-1].href
        # r = requests.get(last_url)
        # print(r.text)
        return resultList
```
到这里为止，基本分析的差不多了，剩下的只是将这些信息存储起来。
# 全部代码

```
# encoding:utf-8
__author__ = "liujinquan"
__date__ = "2018/1/16"

import os
import re
import threading
import traceback
import uuid

import requests
from bs4 import BeautifulSoup as bsp
from sqlalchemy import (
    create_engine, )
from sqlalchemy.orm import sessionmaker

import models


# 从http://www.jlpcn.net/爬取记录片的详细信息,存储到sqlite数据库中
# 读取slqite数据库, 使用you-get工具下载包含pan.baidu.com的链接的纪录片
class SearchMoviesBaiduyun(object):
    def __init__(self):
        super(SearchMoviesBaiduyun, self).__init__()
        self.dbpath = r'sqlite:///F:\liujinquan\python\down_movie\movies.db'
        engine = create_engine(self.dbpath)
        self.Session = sessionmaker(bind=engine)

    def getSoup(self, url):
        '''使用request获取网页源代码,并传入bs'''
        headers = {
            'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
        }
        try:
            r = requests.get(url, headers=headers)
            r.encoding = 'utf-8'
            soup = bsp(r.text, "html.parser")
            return soup
        except Exception as identifier:
            print('getSoup ex:\n%s' % traceback.format_exc())
            return None

    # 分析当前分类的纪录片有多少页
    def findAllLinks(self, url):
        '''
        纪录片分类的地址第一页
        http://www.jlpcn.net/vodtypehtml/1.html
        '''
        links = []
        links.append(url)
        soup = self.getSoup(url)
        if not soup:
            return None
        index1 = url.rfind('.')
        base1 = url[0:index1]
        div = soup.find('div', attrs={"class", "pages"})
        if div:
            pagestr = re.findall(r'当前:1/(.+?)页', div.text)
            if len(pagestr) > 0:
                try:
                    page_cnt = int(pagestr[0])
                    for x in range(2, page_cnt + 1):
                        url_t = "{0}-{1}.html".format(base1, x)
                        links.append(url_t)
                except Exception as ex:
                    traceback.print_exc()
        return links

    # 在分类页面中查找当前页面的纪录片的概要信息
    def findMoives(self, url):
        resultList = []
        soup = self.getSoup(url)
        if not soup:
            return None
        # print(soup.encode_contents())
        li_list = soup.find_all('li', attrs={"class": "mov"})
        for li in li_list:
            imgbox = li.find('img', attrs={"class": "scrollLoading"})
            if imgbox:
                minfo = models.movie_summary()
                minfo.img_url = imgbox["data-url"]
                a_pic = li.find('a', attrs={"class": "pic"})
                if a_pic:
                    minfo.href = a_pic["href"]
                    minfo.title = a_pic["title"]
                    minfo.title = minfo.title.replace(' ', '')
                r1 = li.find('div', attrs={"class": "r1"})
                minfo.update_time = r1.string[5:]
                r3 = li.find_all('div', attrs={"class": "r3"})
                if r3 and len(r3) > 0:
                    for r in r3:
                        if "内容分类" in r.string:
                            minfo.content_category = r.string[5:]
                        elif "频道分类" in r.string:
                            minfo.channel_category = r.string[5:]
                        elif "语言字幕" in r.string:
                            minfo.subtitles = r.string[5:]
                        elif "最后更新" in r.string:
                            minfo.last_update_time = r.string[5:]
                r5 = li.find('div', attrs={"class": "r5"})
                minfo.last_update_time = r5.string[5:]
                print("http://www.jlpcn.net" + minfo.href, minfo.title)
                resultList.append(minfo)
        print(len(li_list))
        return resultList

    # 获取纪录片的详细信息
    def findMovieDetail(self, url):
        resultList = []
        soup = self.getSoup(url)
        if not soup:
            return None

        down_list_2 = soup.find('div', attrs={"id", "down_list_2"})
        if down_list_2:
            scripts = down_list_2.find_all('script')
            if len(scripts) > 0:
                for script in scripts:
                    print(script.string)

        div_list = soup.find_all('div', attrs={"class": "wanpan"})
        for div in div_list:
            a_bd = div.find('a')
            href = a_bd["href"]
            text = a_bd.string
            if not text:
                text = ','.join(a_bd.strings)
            text = text.replace(' ', '')
            # print(href, text)
            detail = models.movie_detail()
            detail.cur_url = url
            detail.title = text
            detail.href = href

            resultList.append(detail)
        # last_url = resultList[-1].href
        # r = requests.get(last_url)
        # print(r.text)
        return resultList

    # 查找某种分类的所有纪录片的概要和详细信息,存储在数据库中
    def searchAllLinks(self, url1):
        base_url = "http://www.jlpcn.net/"
        results = []
        links = self.findAllLinks(url1)
        if len(links) > 0:
            for url in links:
                print("searching -> {0}".format(url))
                movies = self.findMoives(url)
                if len(movies) > 0:
                    for m in movies:
                        self.saveToSummaryTable(
                            self.convertToMovieSummary(base_url, m))
                        url_d = base_url + m.href
                        # print(url_d)
                        details = self.findMovieDetail(url_d)
                        if len(details) > 0:
                            for d in details:
                                # if "pan.baidu.com" in d.href:
                                soup1 = self.getSoup(d.href)
                                if not soup1:
                                    continue
                                title1 = soup1.title.string
                                d.video_name = m.title.replace(
                                    ' ', ''
                                ) + "_" + d.title + self.getMovieType(title1)
                                self.saveToDetailTable(
                                    self.convertToMovieDetail(d))
                                print(d.href, title1, d.video_name)
                                results.append(d)
        # for r in results:
        #     print(r.href, r.title, r.cur_url)
        # print("result len: {0}".format(len(results)))
        # list_url = [x.href for x in results]
        # moveToBaiduYun(list_url)
        # s2 = json.dumps(
        #     results,
        #     default=lambda obj: obj.__dict__,
        #     sort_keys=True,
        #     indent=None,
        #     ensure_ascii=False)
        # print(s2)
        return results

    def getMovieType(self, title):
        if ".avi" in title:
            return ".avi"
        elif ".mp4" in title:
            return ".mp4"
        elif ".rmvb" in title:
            return ".rmvb"
        elif ".mkv" in title:
            return ".mkv"
        elif ".ts" in title:
            return ".ts"
        else:
            return ".avi"

    def saveToDetailTable(self, detail):
        try:
            if isinstance(detail, models.MovieDetail):
                session = self.Session()
                detail.md_id = str(uuid.uuid1())
                session.add(detail)
                session.commit()
                session.close()
        except Exception as identifier:
            print('saveToDetailTable ex:\n%s' % traceback.format_exc())

    def saveToSummaryTable(self, summary):
        try:
            if isinstance(summary, models.MovieSummary):
                session = self.Session()
                summary.m_id = str(uuid.uuid1())
                session.add(summary)
                session.commit()
                session.close()
        except Exception as identifier:
            print('saveToSummaryTable ex:\n%s' % traceback.format_exc())

    def convertToMovieSummary(self, base_url, movie):
        md = models.MovieSummary()
        md.title = movie.title
        md.href = base_url + movie.href
        md.img_url = base_url + movie.img_url
        md.update_time = movie.update_time
        md.content_category = movie.content_category
        md.channel_category = movie.channel_category
        md.subtitles = movie.subtitles
        md.last_update_time = movie.last_update_time
        md.summary = movie.summary
        return md

    def convertToMovieDetail(self, detail):
        d = models.MovieDetail()
        d.cur_url = detail.cur_url
        d.title = detail.title
        d.href = detail.href
        d.video_name = detail.video_name
        return d


if __name__ == '__main__':
    search = SearchMoviesBaiduyun()
    types = [
        32, 20, 29, 31, 36, 30, 28, 27, 24, 19, 25, 39, 38, 22, 21, 37, 40, 23,
        33, 34, 35, 26, 46, 47, 44, 41, 42, 45
    ]
    for t in types:
        url1 = r'http://www.jlpcn.net/vodtypehtml/{0}.html'.format(t)
        search.searchAllLinks(url1)

```
还有对应的model类
```
# coding: utf-8
from sqlalchemy import Column, Text, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class MovieDetail(Base):
    __tablename__ = 'movie_detail'

    md_id = Column(Text(36), primary_key=True)
    cur_url = Column(Text(256))
    title = Column(Text(128))
    href = Column(Text(512))
    video_name = Column(Text(128))
    is_downloaded = Column(Text(3), server_default=text("'0'"))
    down_time = Column(Text(32))


class MovieSummary(Base):
    __tablename__ = 'movie_summary'

    m_id = Column(Text(36), primary_key=True)
    title = Column(Text(50))
    href = Column(Text(255))
    img_url = Column(Text(255))
    update_time = Column(Text(32))
    content_category = Column(Text(128))
    channel_category = Column(Text(128))
    subtitles = Column(Text(512))
    last_update_time = Column(Text(32))
    summary = Column(Text(512))


# 业务中使用的实体类
class movie_summary(object):
    def __init__(self):
        super(movie_summary, self).__init__()
        self.title = ""
        self.href = ""
        self.img_url = ""
        self.update_time = ""
        self.content_category = ""
        self.channel_category = ""
        self.subtitles = ""
        self.last_update_time = ""
        self.summary = ""


class movie_detail(object):
    def __init__(self):
        super(movie_detail, self).__init__()
        self.cur_url = ""
        self.title = ""
        self.href = ""
        self.video_name = ""

```
-------
*2018/1/18 下午*
>前面部分的代码只是采集了电影的百度网盘连接，最终存储在sqlite数据库中，复制这些到浏览器后可直接观看电影。但是如何通过这些链接将电影下载到本地有一些难度。其实在电影详细页面支持迅雷下载，从源代码中也可以搜索到磁力链接。
将这些磁力链接或ed2k链接解析并保存，然后使用aria2或者迅雷下载也是不错的方案
```
# 获取纪录片的详细信息
    def findMovieDetail(self, url):
        resultList = []
        soup = self.getSoup(url)
        if not soup:
            return None
        down_list_2 = soup.find(id="down_list_2")
        if down_list_2:
            # print(down_list_2)
            scripts = down_list_2.find_all(
                'script', text=re.compile(r'ThunderEncode'))
            # print(len(scripts))
            if len(scripts) > 0:
                for script in scripts:
                    s = str(script.string)
                    # 找到磁力链接
                    flag1 = r'ThunderEncode("'
                    index1 = s.index(flag1) + len(flag1)
                    index2 = s.index(r'"', index1)
                    href_str = s[index1:index2]
                    # 找到标题
                    flag2 = r'file_name="'
                    index3 = s.index(flag2) + len(flag2)
                    index4 = s.index(r'"', index3)
                    title_str = s[index3:index4]
                    # 缓存到列表中
                    detail = models.movie_detail()
                    detail.cur_url = url
                    detail.title = title_str.replace(' ', '')
                    detail.href = href_str
                    resultList.append(detail)
        return resultList
```
-------
*2018/2/5 下午*
>获取这些记录片的资源后，就想直接下载自己的硬盘中。
前面的代码中我们可以获取百度链接和磁力链接两种资源方式，磁力资源本身获取的比较少，而且大部分已经过期，及时使用迅雷也无法下载。百度连接的资源前后也尝试过you-get, aria2c等工具，效果都不是很理想。不是速度受限就是根本不能下载。
后来想想还是先转存到百度网盘，然后批量下载。关于百度网盘链接转存到自己的判断网盘，网上有一篇文章，但我没有尝试成功，只好采用selenium的方式。

```
# encoding:utf-8
__author__ = "liujinquan"
__date__ = "2018/1/28"

import datetime
import json
import logging
import os
import re
import threading
import time
import traceback
import urllib.parse
import uuid

import requests
from bs4 import BeautifulSoup as bsp
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import models
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains

chromedriver = "C:/Users/Administrator/AppData/Local/Google/Chrome/Application/chromedriver.exe"
os.environ["webdriver.chrome.driver"] = chromedriver

profile_dir = r"C:\Users\Administrator\AppData\Local\Mozilla\Firefox\Profiles\cqupe01d.default"
profile = webdriver.FirefoxProfile(profile_dir)
driver = webdriver.Firefox(profile)

# from selenium import webdriver
# from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# dcap = dict(DesiredCapabilities.PHANTOMJS)  #设置userAgent
# dcap["phantomjs.page.settings.userAgent"] = (
#     "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36"
# )


class MoveToBaiduYun(object):
    def __init__(self):
        super(MoveToBaiduYun, self).__init__()
        self.dbpath = r'sqlite:///F:\liujinquan\python\down_movie\movies.db'
        self.engine = create_engine(self.dbpath)
        self.Session = sessionmaker(bind=self.engine)

    def getAllBaiduLinks(self):
        try:
            session = self.Session()
            links = session.query(models.MovieDetail.href).all()
            session.commit()
            session.close()
            print(len(links))
            return list(links)
        except Exception as identifier:
            print('getAllBaiduLinks ex:\n%s' % traceback.format_exc())
            return None

    def moveToBaiduYun(self, list_url):
        # url = 'https://pan.baidu.com/s/1o8ID1hC'
        # 这里可以用Chrome、Phantomjs等，如果没有加入环境变量，需要指定具体的位置
        # options = webdriver.ChromeOptions()
        # options.add_argument(
        #     "--user-data-dir=" +
        #     r"C:/Users/Administrator/AppData/Local/Google/Chrome/User Data")
        # driver = webdriver.Chrome(
        #     executable_path=chromedriver, options=options)
        # driver.maximize_window()

        # driver = webdriver.PhantomJS(
        #     executable_path='C:\Python\Python36\Scripts\phantomjs.exe',
        #     desired_capabilities=dcap)  #加载网址
        # driver.maximize_window()

        profile = webdriver.FirefoxProfile(profile_dir)
        driver = webdriver.Firefox(profile)
        driver.maximize_window()

        for url in list_url:
            driver.get(url)
            print('开始登录:' + url)
            try:
                save_to_pans = driver.find_element_by_class_name(
                    "bar").find_elements_by_css_selector(
                        "[class='g-button g-button-blue']")
                print(len(save_to_pans))
                for tag in save_to_pans:
                    print(tag.text)
                    time.sleep(1)
                    if tag.get_attribute("data-button-id") == u'b1':
                        print("find target.")
                        time.sleep(1)
                        tag.click()
                        # for x in range(1, 10):
                        #     time.sleep(1)
                        #     tag.click()
                        time.sleep(1)
                        driver.switch_to_default_content()
                        save_buttons = driver.find_element_by_id(
                            "fileTreeDialog").find_element_by_css_selector(
                                "[class='dialog-footer g-clearfix']"
                            ).find_elements_by_css_selector(
                                "[class='g-button g-button-blue-large']")
                        print(len(save_buttons))
                        for btn in save_buttons:
                            if btn.get_attribute("data-button-id") == u'b13':
                                print("find target again!")
                                time.sleep(1)
                                btn.click()
                        break
                time.sleep(3)
            except Exception as identifier:
                logging.error('down_movies ex:\n%s' % traceback.format_exc())
        return driver.get_cookies()

    def moveToBaiduYun_OldUrl(self, list_url):
        profile = webdriver.FirefoxProfile(profile_dir)
        driver = webdriver.Firefox(profile)
        driver.maximize_window()

        for url in list_url:
            driver.get(url)
            print('开始登录:' + url)
            try:
                # save_to_pans = driver.find_element_by_class_name(
                #     "bar").find_elements_by_css_selector(
                #         "[class='g-button g-button-blue']")
                save_to_pans = driver.find_element_by_id('emphsizeButton')
                if save_to_pans:
                    print("find target")
                    print(save_to_pans.text)
                    time.sleep(0.5)
                    save_to_pans.click()
                    time.sleep(0.5)

                    driver.switch_to_default_content()
                    save_buttons = driver.find_element_by_id('_disk_id_8')
                    if save_buttons:
                        print("find target again!")
                        time.sleep(0.5)
                        save_buttons.click()

                time.sleep(3)

            except Exception as identifier:
                logging.error('down_movies ex:\n%s' % traceback.format_exc())
        return driver.get_cookies()


if __name__ == '__main__':
    move = MoveToBaiduYun()
    links = move.getAllBaiduLinks()
    print(links[0], links[1])
    # links = [x[0] for x in links if 'pan.baidu.com' in x[0]]
    # print(len(links))
    # move.moveToBaiduYun(links)
    links = [x[0] for x in links if 'yun.baidu.com' in x[0]]
    print(len(links))
    move.moveToBaiduYun_OldUrl(links)

```



