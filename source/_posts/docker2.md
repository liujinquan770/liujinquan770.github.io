---
title: DOCKER笔记2 docker安装步骤
date: 2019-03-25 19:19:19
modified: 
tags: [docker]
categories: docker
---

记录DOKCER的标准安装方式。

![示例图片](docker2/5828001.jpg)

<!--more-->

## 安装docker和docker-compose
**1.安装 docker**  
https://docs.docker.com/install/linux/docker-ce/ubuntu/  

**A. Uninstall old versions**  
$ sudo apt-get remove docker docker-engine docker.io containerd runc  

**B. SET UP THE REPOSITORY**   
$ sudo apt-get update  
$ sudo apt-get install \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common  
$ curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -  
$ sudo add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"  

**C. INSTALL DOCKER CE**  
$ sudo apt-get update  
$ sudo apt-get install docker-ce docker-ce-cli containerd.io  

**2.安装 docker-compose**  
https://docs.docker.com/compose/install/  

**A.  Install Compose on Linux systems**  
$ sudo curl -L "https://github.com/docker/compose/releases/download/1.23.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose  
$ sudo chmod +x /usr/local/bin/docker-compose

**3.其他相关命令**  
**A. 关闭所有正在运行容器**  
$ sudo docker ps | awk  '{print $1}' | xargs docker stop  
**B. 删除所有容器应用**  
$ sudo docker ps -a | awk  '{print $1}' | xargs docker rm  
**C. 或者**  
$ sudo docker rm $(sudo docker ps -a -q)  
$ sudo docker rmi $(sudo docker images -a -q)


**4.关于docker-compose启动顺序**   
https://docs.docker.com/compose/startup-order/  
重点关注vishnubob/wait-for-it  

**5.关于docker-compose环境变量**  
>env_file和environment中定义的环境变量是传给container用的而不是在docker-compose.yml中的环境变量用的   
docker-compose.yml中的环境变量${VARIABLE:-default}引用的是在.env中定义的或者同个shell export出来的   
 
>建议env_file 引入的文件名为.env,最好不要使用其他名称 
优点: .env文件变更会实时更新docker-compose中的引用，使用其他名称不会实时更新docker-compose中的引用,使用其他名称在docker-compose中引用有时会WARNING: The DB_DIR variable is not set. Defaulting to a blank string.
缺点: 自定义名称不方便

