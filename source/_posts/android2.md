---
title: ANDROID异步日志
date: 2018-06-22 09:03:55
tags: [android,log]
categories: android
---

&emsp;&emsp;开发中如果不需要记录文本日志，使用Blankj/AndroidUtilCode提供的日志工具即可，但是有些情况需要记录文本日志，则使用slf4j和logback更合适。  
&emsp;&emsp;android使用slf4j和logback异步方式记录日志不会占用主界面线程的时间

![示例图片](android2/20180622.jpg)

<!--more-->

# 1 引入开源库

``` gradle
api 'org.slf4j:slf4j-api:1.7.21'
api 'com.github.tony19:logback-android-core:1.1.1-5'
api 'com.github.tony19:logback-android-classic:1.1.1-5'
```

# 2 编写日志配置文件
在asset目录下添加logback.xml日志配置文件
``` xml
<!--debug属性用来决定是否打印logback的日志信息-->
<configuration debug='false'>

    <!--声明一个属性,用来指定log文件存放的路径-->
    <property name="LOG_DIR" value="/sdcard/qifei_orange_log" />

    <!--声明一个时间戳-->
    <timestamp datePattern="yyyyMMdd" key="today" />

    <!--用于在控制台输出的Appender-->
    <appender name="LOGCAT" class="ch.qos.logback.classic.android.LogcatAppender">
        <encoder>
            <pattern>%-5relative [%thread][%file:%M:%line] - %msg%n</pattern>
        </encoder>
    </appender>

    <!--声明一个FileAppender-->
    <appender name="BASE_FILE" class="ch.qos.logback.core.FileAppender">
        <!--初始化的时候不创建文件,在第一次使用的时候创建文件-->
        <lazy>true</lazy>
        <!--log追加到文件,否则覆盖文件-->
        <append>true</append>
        <!--用来保存log的文件全路径-->
        <file>${LOG_DIR}/base.log</file>
        <!--输出log的格式-->
        <encoder>
            <!--<pattern>%d{HH:mm:ss.SSS} [%thread] %-5level %logger{36} [%file:%line] - %msg%n</pattern>-->
            <pattern>%date [%thread] %-5level %logger{36} [%file:%line] - %msg%n</pattern>
        </encoder>
    </appender>

    <!--声明一个RollingFileAppender-->
    <appender name="BASE_ROLL_FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>${LOG_DIR}/qifei.orange.${today}.log</file>
        <append>true</append>
        <encoder>
            <pattern>%date %-5relative [%thread] %-5level %logger{36} [%file:%M:%line] - %msg%n
            </pattern>
        </encoder>

        <rollingPolicy class="ch.qos.logback.core.rolling.TimeBasedRollingPolicy">
            <fileNamePattern>${LOG_DIR}/qifei.orange.%d{yyyy-MM-dd}.log</fileNamePattern>
            <!--最大保存7天的日志-->
            <maxHistory>7</maxHistory>
        </rollingPolicy>

        <!--文件大于10mb,切换文件-->
        <triggeringPolicy class="ch.qos.logback.core.rolling.SizeBasedTriggeringPolicy">
            <maxFileSize>10MB</maxFileSize>
        </triggeringPolicy>
    </appender>

    <!--  异步输出，异步的log片段必须在同步段后面，否则不起作用  -->
    <appender name="BASE_ROLL_FILE_ASYNC" class="ch.qos.logback.classic.AsyncAppender">
        <!-- 不丢失日志.默认的,如果队列的80%已满,则会丢弃TRACT、DEBUG、INFO级别的日志 -->
        <discardingThreshold>0</discardingThreshold>
        <!-- 更改默认的队列的深度,该值会影响性能.默认值为256 -->
        <queueSize>${log.queueSize}</queueSize>
        <!-- 添加附加的appender,最多只能添加一个 -->
        <appender-ref ref="BASE_ROLL_FILE" />
    </appender>

    <!--log_orange-->
    <logger name="log_orange" level="TRACE">
        <appender-ref ref="BASE_ROLL_FILE_ASYNC" />
    </logger>


    <!-- Write INFO (and higher-level) messages to the log file -->
    <root level="TRACE">
        <appender-ref ref="LOGCAT" />
    </root>

    <!--<includes>-->
    <!--<include resource="assets/logback.xml" />-->
    <!--</includes>-->

    <!--支持的level-->
    <!--TRACE-->
    <!--DEBUG-->
    <!--INFO-->
    <!--WARN-->
    <!--ERROR-->

    <!--<pattern>
      %d{yyyy-MM-dd HH:mm:ss} [%level] - %msg%n
      Logger: %logger
      Class: %class
      File: %file
      Caller: %caller
      Line: %line
      Message: %m
      Method: %M
      Relative: %relative
      Thread: %thread
      Exception: %ex
      xException: %xEx
      nopException: %nopex
      rException: %rEx
      Marker: %marker
      %n
  </pattern>-->

    <!--引用其他位置的配置信息-->
    <!--<includes>-->
    <!--<include file="/sdcard/foo.xml"/>-->
    <!--<include resource="assets/config/test.xml"/>-->
    <!--<include resource="AndroidManifest.xml"/>-->

    <!--<include file="/sdcard/logback/logback-test.xml"/>-->
    <!--<include file="/sdcard/logback/logback.xml"/>-->
    <!--<include resource="AndroidManifest.xml"/>-->
    <!--<include resource="assets/logback-test.xml"/>-->
    <!--<include resource="assets/logback.xml"/>-->
    <!--</includes>-->
</configuration>
```
>需要注意上文中BASE_ROLL_FILE_ASYNC节点的写法。

# 3 日志工具类和使用

``` java
public class LogUtil {

    public static Logger getLogger() {
        Logger logger = LoggerFactory.getLogger("log_orange");
        return logger;
    }
}
```
调用方法
``` java
 LogUtil.getLogger().debug("left " + t.tick + " seconds");
```