---
title: PYTHON笔记11 anaconda命令
date: 2018-09-01 13:54:21
modified: 
tags: [python]
categories: python
---

安装miniconda后一些常用命令需要记住。

![示例图片](python11/2018091.jpg)

<!--more-->

## 创建自己的虚拟环境
```python
conda create -n learn python=3
# 这里conda会自动找3中最新的版本下载，或者指定版本
conda create -n learn python=3.6.5
```

## 切换环境
```
activate learn
```

## 查看所有的环境
```
conda env list
```

## 查看当前环境中所有安装了的包
```
conda list 
```

## 常用命令
```
activate // 切换到base环境

activate learn // 切换到learn环境

conda create -n learn python=3 // 创建一个名为learn的环境并指定python版本为3(的最新版本)

conda env list // 列出conda管理的所有环境

conda list // 列出当前环境的所有包

conda install requests 安装requests包

conda remove requests 卸载requets包

conda remove -n learn --all // 删除learn环境及下属所有包

conda update requests 更新requests包

conda env export > environment.yaml // 导出当前环境的包信息

conda env create -f environment.yaml // 用配置文件创建新的虚拟环境

```

## pip离线安装命令
新版pip下载安装包命令：
pip download  -r requirements.txt  -d  /tmp/paks/

在linux下

>1.下载指定的包到指定文件夹。
pip list #查看安装的包  
pip freeze > requirements.txt     
将已经通过pip安装的包的名称记录到 requirements.txt文件中
创建存放安装包的目录：  
mkdir /packs  
pip install   --download   /packs  pandas(存放一个pandas包)    
或  
pip install   --download   /packs -r requirements.txt（存放requirements.txt列出的所有包）


>2.安装指定的离线包
pip install   --no-index   --find-links=/packs/   pandas 或      
pip install   --no-index   --find-links=/packs/   -r   requirements.txt    （也可能是 --find-link）
 
在windows下与linux下类似



## pip和conda导出导入依赖包
1.  
pip批量导出包含环境中所有组件的requirements.txt文件
pip freeze > requirements.txt
2.  
pip批量安装requirements.txt文件中包含的组件依赖
pip install -r requirements.txt
3.  
conda批量导出包含环境中所有组件的requirements.txt文件
conda list -e > requirements.txt
4.  
pip批量安装requirements.txt文件中包含的组件依赖
conda install --yes --file requirements.txt
5.  
通过本地安装包安装
如果出现网络问题或者无法联网可以先在Anaconda的网站上下载安装包,然后通过--use-local进行本地安装。
conda install --use-local ffmpeg-2.7.0-0.tar.bz2
