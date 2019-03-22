---
title: HADOOP笔记1 HADOOP单机安装
date: 2018-11-05 08:45:45
modified: 
tags: [HADOOP]
categories: HADOOP
---

入门学习笔记

![示例图片](hadoop1/20181105.jpg)
<!--more-->

## 安装虚拟机
安装后使用NAT和桥接模式联网，并安装net-tools
```bash
yum install net-tools
```
通过rpm -qa | grep ssh 检查cent os 是否安装了ssh server和ssh client
如果没有安装则先安装ssh
```bash
yum install openssh-clients
yum install openssh-server
```
远程登录工具我选用的是SecureCRT

## 创建hadoop用户
```bash
useradd -m hadoop -s /bin/bash 
passwd hadoop    #为hadoop用户设置密码，我们设置为hadoop，方便
```

## 配置SSH无密码访问
1.首先我们需要进入/home/hadoop/.ssh目录下，如果这个目录不存在，需要执行一下ssh localhost   这样就会生成这个目录。  
2.执行以下命令，创建密钥并且将密钥加入授权：
```bash
cd ~/.ssh/                       # 若没有该目录，请先执行一次ssh localhost
ssh-keygen -t dsa                 # 会有提示，都按回车就可以
cat id_dsa.pub >> authorized_keys   # 加入授权
chmod 600 ./authorized_keys       # 修改文件权限，如果不改，无法通过，原因好像是cent os的权限验证比较严格
```
3.在root用户下修改/etc/ssh/sshd_config文件（取消以下三个变量的注释）  
```bash
vi /etc/ssh/sshd_config
```
```bash
RSAAuthentication yes
PubkeyAuthentication yes
AuthorizedKyesFile      .ssh/authorized_keys
```
重启sshd服务
```bash
service sshd restart
```
4.切换到hdoop用户，接下来，输入ssh localhost测试一下无密码登录，直接enter就可以，无需密码

## 安装JAVA环境
1.通过 yum 进行安装 JDK
```bash
yum install java-1.7.0-openjdk java-1.7.0-openjdk-devel
```
通过rpm -ql java-1.7.0-openjdk-devel | grep '/bin/javac'找到安装路径,这个路径后面需要设置到环境变量
设置全局环境变量：
```bash
vi /etc/profile
```
然后添加
```bash
export JAVA_HOME=/usr/lib/jvm/java-1.7.0-openjdk-1.7.0.191-2.6.15.4.el7_5.x86_64
export PATH=$JAVA_HOME/bin:$PATH
export CLASSPATH=.:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar
```

## 单机模式安装
1.使用SecureCRT的sftp上传hadoop安装包  
Hadoop下载地址：
http://archive.apache.org/dist/hadoop/core/
2.使用root账号，进入/home/hadoop目录下，解压安装文件到/usr/local/hadoop下
```bash
tar -zxvf hadoop-2.6.0.tar.gz -C /usr/local
```
修改权限
```bash
mv hadoop-2.6.0/ hadoop/   #更改文件夹名称
chown -R hadoop:hadoop ./hadoop   #修改权限
```
3.验证单机模式是否安装成功  
进入/usr/local/hadoop/bin目录下，执行./hadoop version