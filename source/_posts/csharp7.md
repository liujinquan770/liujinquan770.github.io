---
title: C#笔记7 ASPNET CORE开发记录
date: 2018-09-11 16:24:43
modified: 
tags: [C#]
categories: C#
---

记录 aspnet core的web开发中的一些坑。

![示例图片](csharp7/20180911.jpg)

<!--more-->

## Csc”任务不支持“SharedCompilationId”参数
未能使用“Csc”任务的输入参数初始化该任务。

“Csc”任务不支持“SharedCompilationId”参数。请确认该参数存在于此任务中，并且是可设置的公共实例属性。

解决办法：  
Nuget上安装Microsoft.Net.Compilers -Version 最新版即可