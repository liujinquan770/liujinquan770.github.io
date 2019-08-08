---
title: java笔记2 一次java程序维护
date: 2019-08-08 21:18:22
modified: 
tags: [java]
categories: java
---

使用jar命令在LINUX服务器部署springboot2的JAR包

![示例图片](java2/4495511.jpg)
<!--more-->


## 服务器地址，账号密码
IP地址分别是10.143.62.231,10.143.62.232,10.143.62.233,10.143.62.234
账号密码是root/linux


## 其他
1.nginx的路径为/usr/local/nginx/nginx,里面有所部署网站的部署信息  
2.网站的登录账号密码是admin/admin
3.除了网站，还有OPC和DPC需要启动，在/opt/foxconn/code
4.cloudera manager的url是http://10.143.62.231:7180
5.esgyndb的jdbc驱动的位置是 /opt/trafodion/esgyndb/export/lib, 使用是需要配置的url是 jdbc:t4jdbc://10.143.62.232:23400/:, 文件是jdbcT4-2.7.0.jar.
数据库的账号密码是trafodion/traf123
6.datagrip不能使用最新版，可用的版本是2018.2