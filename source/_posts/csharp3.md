---
title: C#笔记3 PostGreSQL安装和简单使用
date: 2018-08-17 10:08:26
modified: 
tags: [C#]
categories: C#
---

记录PostgreSQL在windows7X64下安装，并使用EF调用过程。  

![示例图片](csharp3/20180817.jpg)

<!--more-->

## 下载
1.从 https://www.postgresql.org/ 下载windows版本的安装文件  
2.安装前确认 <b><font color=#00ffff>防火墙服务(Windows Firewall)</font></b> 已经运行，否则后面可能会报错  
3.安装后创建测试表

## EF访问数据库
1.安装我们需要的Nuget包， npgsql 和 EntityFramework6.Npgsql  
2.安装VS插件NpgSql PostgreSQL Integration插件(连接postgresql数据库使用)
3.在app.config内添加
```xml
  <system.data>
    <DbProviderFactories>
      <add name="Npgsql Data Provider" invariant="Npgsql" description="Data Provider for PostgreSQL" type="Npgsql.NpgsqlFactory, Npgsql" />
    </DbProviderFactories>
  </system.data>
```
否则运行时报出异常"The ADO.NET provider with invariant name 'Npgsql' is either not registered in the machine or application config file, or could not be loaded"

## C#访问代码
1.采用dbfirst创建连接和edmx文件  
2.编写测试代码
``` csharp
private void button1_Click(object sender, EventArgs e)
{
    int count = 0;
    using(testEntities context = new testEntities())
    {
        count = context.Device.Count();
    }
    MessageBox.Show(count.ToString());
}
```

## PYTHON访问代码
```python
#encoding:utf8
# sqlacodegen postgresql://postgres:123456@localhost:5432/test > modles.py
from sqlalchemy import and_, create_engine, func, or_
from sqlalchemy.orm import sessionmaker

from modles import Device

engine = create_engine('postgresql://postgres:123456@localhost:5432/test',echo=False)
Session = sessionmaker(bind=engine)
session = Session()
query = session.query(Device)
result = query.filter(and_(Device.DevCode=='000498', Device.DevStatus==1)).first()
print(result.DevCode)
print(len(query.all()))
```
