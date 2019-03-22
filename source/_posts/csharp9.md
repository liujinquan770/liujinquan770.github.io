---
title: C#笔记9 在C#中使用Google ProtoBuf
date: 2018-10-26 13:30:13
modified: 
tags: [C#]
categories: C#
---

项目中有个设备的通信协议采用google protobuf封装,因此需要学习一下.

![示例图片](csharp9/201801026.jpg)

<!--more-->

使用ProtoBuf主要有两个操作,序列化和解序列化,这两个操作都需要协议描述文件也就是.proto文件,如果要使用protobuf存储自定义的数据,就要自己编写proto文件.

## 安装Google.Protobuf和Google.Protobuf.Tools的Nuget包

## 在Google.Protobuf.Tools下找到编译工具protoc.exe
这个工具的主要作用是将.proto文件转换成同名的cs文件.   
程序所需的参数说明参考 https://developers.google.com/protocol-buffers/docs/reference/csharp-generated 

## 准备好协议描述文件xxx.proto
关于.proto的详细说明可以从 https://developers.google.com/protocol-buffers/ 上找到.

使用protoc.exe转换成cs文件
```bat
@echo off 
color 0A
::指定起始文件夹
set DIR="%cd%"
echo DIR=%DIR%

:: 参数 /R 表示需要遍历子文件夹,去掉表示不遍历子文件夹
:: %%f 是一个变量,类似于迭代器,但是这个变量只能由一个字母组成,前面带上%%
:: 括号中是通配符,可以指定后缀名,*.*表示所有文件
for /R %DIR% %%f in (*.proto) do ( 
	echo %%f
	.\protoc.exe --proto_path=%DIR% --csharp_out=%DIR% %%f
)
pause
```

## 序列化与反序列化
序列化
```csharp
public static byte[] GetBytesFromMessage(Message msg)
{
    return msg.ToByteArray();
}
```
反序列化
```csharp
public static Message ParseFromBytes(byte[] bytes)
{
    Message msg = Message.Parser.ParseFrom(bytes);
    return msg;
}
```