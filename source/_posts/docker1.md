---
title: DOCKER笔记1 常用docker-compose.yml
date: 2019-03-16 17:20:58
modified: 
tags: [docker]
categories: docker
---

记录DOKCER的常用命令，镜像，配置文件等



![示例图片](docker1/6390001.jpg)

<!--more-->

## 单机版KAFKA
```yaml
version: "2"
services:
  zookeeper:
    image: wurstmeister/zookeeper ## 镜像
    restart: always
    ports:
      - "2181:2181" ## 对外暴露的端口号
  kafka:
    image: wurstmeister/kafka ## 镜像
    restart: always
    volumes:
      - /etc/localtime:/etc/localtime ## 挂载位置（kafka镜像和宿主机器之间时间保持一直）
    ports:
      - "9092:9092"
    environment:
      KAFKA_ADVERTISED_HOST_NAME: 192.168.0.105 ## 修改:宿主机IP
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181 ## 卡夫卡运行是基于zookeeper的
  # kafka-manager:
  #   image: sheepkiller/kafka-manager ## 镜像：开源的web管理kafka集群的界面
  #   environment:
  #     ZK_HOSTS: 192.168.56.102 ## 修改:宿主机IP
  #   ports:
  #     - "9000:9000" ## 暴露端口
  collect_python:
    tty: true
    build: ./app
    restart: always
    volumes:
      - ./app:/app
    depends_on:
      - zookeeper
      - kafka
    entrypoint: "python spindle_predict.py"
```

## 集群版KAFKA
```yaml
version: '3.1'

services:
  zoo1:
    image: zookeeper
    restart: always
    hostname: zoo1
    ports:
      - 2181:2181
    environment:
      ZOO_MY_ID: 1
      ZOO_SERVERS: server.1=0.0.0.0:2888:3888 server.2=zoo2:2888:3888 server.3=zoo3:2888:3888
    volumes: 
      - /storage/zk1/zkdata/:/data
      - /storage/zk1/zkdatalog/:/datalog

  zoo2:
    image: zookeeper
    restart: always
    hostname: zoo2
    ports:
      - 2182:2181
    environment:
      ZOO_MY_ID: 2
      ZOO_SERVERS: server.1=zoo1:2888:3888 server.2=0.0.0.0:2888:3888 server.3=zoo3:2888:3888
    volumes: 
      - /storage/zk2/zkdata/:/data
      - /storage/zk2/zkdatalog/:/datalog

  zoo3:
    image: zookeeper
    restart: always
    hostname: zoo3
    ports:
      - 2183:2181
    environment:
      ZOO_MY_ID: 3
      ZOO_SERVERS: server.1=zoo1:2888:3888 server.2=zoo2:2888:3888 server.3=0.0.0.0:2888:3888
    volumes: 
      - /storage/zk3/zkdata/:/data
      - /storage/zk3/zkdatalog/:/datalog

  kafka1:
    image: wurstmeister/kafka
    restart: always
    hostname: kafka1
    ports:
      - "9092:9092"
    depends_on:
      - zoo1
      - zoo2
      - zoo3
    environment:
      #KAFKA_ADVERTISED_HOST_NAME: 192.168.99.100
      #KAFKA_CREATE_TOPICS: "test:1:1"
      KAFKA_BROKER_ID: 1
      KAFKA_LOG_RETENTION_BYTES: 1099511627776
      KAFKA_LOG_DIRS: /kafka/logs
      KAFKA_LISTENERS: PLAINTEXT://:9092
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://192.168.1.97:9092
      KAFKA_ZOOKEEPER_CONNECT: zoo1:2181,zoo2:2182,zoo3:2183
      KAFKA_LOG_RETENTION_HOURS: 720
      #KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: INSIDE:PLAINTEXT,OUTSIDE:PLAINTEXT
      #KAFKA_INTER_BROKER_LISTENER_NAME: INSIDE
    volumes:
      - "/storage/kafka1:/kafka/logs"

  kafka2:
    image: wurstmeister/kafka
    restart: always
    hostname: kafka2
    ports:
      - "9093:9092"
    depends_on:
      - zoo1
      - zoo2
      - zoo3
    environment:
      #KAFKA_ADVERTISED_HOST_NAME: 192.168.99.100
      #KAFKA_CREATE_TOPICS: "test:1:1"
      KAFKA_BROKER_ID: 2
      KAFKA_LOG_RETENTION_BYTES: 1099511627776
      KAFKA_LOG_DIRS: /kafka/logs
      KAFKA_LISTENERS: PLAINTEXT://:9092
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://192.168.1.97:9093
      KAFKA_ZOOKEEPER_CONNECT: zoo1:2181,zoo2:2182,zoo3:2183
      KAFKA_LOG_RETENTION_HOURS: 720
      #KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: INSIDE:PLAINTEXT,OUTSIDE:PLAINTEXT
      #KAFKA_INTER_BROKER_LISTENER_NAME: INSIDE 
    volumes:
      - "/storage/kafka2:/kafka/logs"

  kafka3:
    image: wurstmeister/kafka
    restart: always
    hostname: kafka3
    ports:
      - "9094:9092"
    depends_on:
      - zoo1
      - zoo2
      - zoo3
    environment:
      #KAFKA_ADVERTISED_HOST_NAME: 192.168.99.100,
      #KAFKA_CREATE_TOPICS: "test:1:1",
      KAFKA_BROKER_ID: 3
      KAFKA_LOG_RETENTION_BYTES: 1099511627776
      KAFKA_LOG_DIRS: /kafka/logs
      KAFKA_LISTENERS: PLAINTEXT://:9092
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://192.168.1.97:9094
      KAFKA_ZOOKEEPER_CONNECT: zoo1:2181,zoo2:2182,zoo3:2183
      KAFKA_LOG_RETENTION_HOURS: 720
      #KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: INSIDE:PLAINTEXT,OUTSIDE:PLAINTEXT
      #KAFKA_INTER_BROKER_LISTENER_NAME: INSIDE
    volumes:
      - "/storage/kafka3:/kafka/logs"
```
