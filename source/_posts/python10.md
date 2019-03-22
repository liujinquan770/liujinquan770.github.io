---
title: PYTHON笔记8 ubuntu下uWSGI部署flask
date: 2018-08-28 16:56:44
modified: 
tags: [python]
categories: python
---

想研究一下linux网站的部署，总是遇到坑。干脆就记录一下采坑的过程。

![示例图片](python10/20180828.jpg)

<!--more-->

## 部署flask

网上有许多讲ubuntu部署flask的文章，都有描述uWSGI安装和配置的步骤，但是参照这些文章都没有成功。最后找到官方的说明文档,一步一步尝试才有了效果。  
先贴一下官方文档的网址https://uwsgi-docs.readthedocs.io/en/latest/WSGIquickstart.html  

## 安装步骤
uWSGI is a (big) C application, so you need a C compiler (like gcc or clang) and the Python development headers.
```bash
apt-get install build-essential python-dev
```
You have various ways to install uWSGI for Python:
```bash
pip install uwsgi
```

## 部署flask
Save the following example as myflaskapp.py:
```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def index():
    return "<span style='color:red'>I am app 1</span>"
```
执行命令
```bash
uwsgi --http-socket 127.0.0.1:3031 --wsgi-file myflaskapp.py --callable app --processes 4 --threads 2 --stats 127.0.0.1:9191
```
到目前为止网站基本能运行起来了。  

不过大多数人不习惯每次写这么长的命令,官网也提供了配置文件的方法, 可参考https://uwsgi-docs.readthedocs.io/en/latest/Configuration.html?highlight=ini#ini-files  

在myflaskapp.py所在目录下创建文件uwsgi.ini文件,把上述的命令中的参数写入即可
```ini
[uwsgi]
http-socket = 127.0.0.1:3031
wsgi-file = myflaskapp.py
callable = app
processes = 4
threads = 2
stats = 127.0.0.1:9191
```
最后在shell中调用
```bash
uwsgi --ini uwsgi.ini
```

nginx相关配置文档的网址是https://uwsgi-docs.readthedocs.io/en/latest/Nginx.html  
但是我一直没有配置成功,后面再研究吧

>2018/08/30  
nginx与uWSGI配置还是没有测试成功, 故顺便学了nginx的反向代理。还有负载均衡的配置方法需要学习.

## supervisor和systemd
