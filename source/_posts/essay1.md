---
title: 杂文1 修改DNS方法加速github访问速度
date: 2019-08-08 21:18:22
modified: 
tags: [eassy]
categories: essay
---

    GitHub在国内访问速度慢的问题原因有很多，但最直接和最主要的原因是GitHub的分发加速网络的域名遭到dns污染。
    
    今天我们就介绍通过修改系统hosts文件的办法，绕过国内dns解析，直接访问GitHub的CDN节点，从而达到加速的目的。

感谢 https://zhuanlan.zhihu.com/p/65154116

![示例图片](essay1/96871.jpg)
<!--more-->

## 查询GITHUB相关网址IP
打开http://IPAddress.com网站，查询下面3个网址对应的IP地址
1. http://github.com
2. http://assets-cdn.github.com
3. http://github.global.ssl.fastly.net

## 修改本地电脑HOSTS
host文件的路径是 C:\Windows\System32\drivers\etc
将查询到的网址与IP对应关系增加到host文件(因为权限问题，可能需要拷贝到非系统文件夹)

192.30.253.112 http://github.com  
151.101.184.133 http://assets-cdn.github.com  
151.101.185.194 http://github.global.ssl.fastly.net  

## 刷新系统dns缓存
在命令行窗口输入命令：<b>ipconfig /flushdns</b> 回车后执行刷新本地dns缓存数据即可。

目前这种方法至少提高几十K的下载速率。