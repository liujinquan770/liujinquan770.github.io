---
title: C#笔记6 ASPNETCORE2在UBUNTU安装和部署
date: 2018-08-27 10:50:43
modified: 
tags: [C#]
categories: C#
---

最近想研究docker部署dotnetcore网站，发现docker都是基于linux命令的。所以决定从ubuntu开始学习。

![示例图片](csharp6/20180827.jpg)

<!--more-->

## 参考文章
1.ubuntu安装.netcore > https://blog.csdn.net/qq_36446887/article/details/80722614  
2.nginx反向代理 > https://www.cnblogs.com/ayzhanglei/p/5635549.html

## 安装ubuntu虚拟机

## 安装aspnetcore sdk
```bash
wget -qO- https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > microsoft.asc.gpg
sudo mv microsoft.asc.gpg /etc/apt/trusted.gpg.d/
wget -q https://packages.microsoft.com/config/ubuntu/18.04/prod.list
sudo mv prod.list /etc/apt/sources.list.d/microsoft-prod.list
```
然后
```bash
sudo apt-get install apt-transport-https
sudo apt-get update
sudo apt-get install dotnet-sdk-2.1
```

## 安装nginx
```bash
sudo apt-get install nginx
```
授予配置文件读写权限
```bash
sudo chmod 777 /etc/nginx/sites-available/default
```
修改配置文件location /节点
```bash
location / {
        proxy_pass http://localhost:5000;#core你自己配置的端口
    }
```
重新启动
```
sudo nginx -c /etc/nginx/nginx.conf
sudo service nginx stop
sudo service nginx start
```

## 编写asp.net core网站并拷贝到ubuntu上编译,发布
使用FTP上传源代码  
然后
```
dotnet restore  
dotnet run  
dotnet publish  
```
最后切换到发布目录下
```
nohup donet webapplication1.dll
```



