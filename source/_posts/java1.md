---
title: java笔记1 jar命令运行网站
date: 2019-07-28 20:38:20
modified: 
tags: [java]
categories: java
---

使用jar命令在LINUX服务器部署springboot2的JAR包

![示例图片](java1/6248261.jpg)
<!--more-->

## 启动和停止
启动脚本start.sh
```bash
#!/bin/bash
nohup java -jar lol.jar &
```  
停止脚本stop.sh
```bash
 #!/bin/bash
PID=$(ps -ef | grep lol.jar | grep -v grep | awk '{ print $2 }')
if [ -z "$PID" ]
then
    echo Application is already stopped
else
    echo kill $PID
    kill $PID
fi
```  
接着，我们需要赋予这两个脚本的权限:  
>chmod 755 start.sh stop.sh

最后，我们执行以下命令后台运行项目：  
>./start.sh

查看日志
>tail -f nohup.out

