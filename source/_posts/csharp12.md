---
title: C#笔记12 C#高性能写文件
date: 2019-01-21 20:37:17
modified: 
tags: [C#]
categories: C#
---

C#异步方式高速写文件,在高频采集数据的时候非常有用.  
除了写文件，还有效率更高的方式,比如文件数据库,网络数据库,NOSQL数据库。目前只尝试过Sqlite, MySql, MongDb.

从效率上讲 MongDb>Mysql>Sqlite>本地文件

![示例图片](csharp12/20190121.jpg)

<!--more-->

贴出部分示例代码
```csharp
private void WriteFile(string path, byte[] buffer)
{
    FileStream fs = new FileStream(path, FileMode.OpenOrCreate, FileAccess.ReadWrite, FileShare.ReadWrite, 4096, true);
    fs.BeginWrite(buffer, 0, buffer.Length, new AsyncCallback(Callback), fs);
}

private void Callback(IAsyncResult result)
{
    FileStream stream = (FileStream)result.AsyncState;
    stream.EndWrite(result);
    stream.Close();
}
```

MYSQL(SQLITE插入数据时候使用prepare语句和事务能显著提升速度)
```CSHARP
string _conn_str = @"server = localhost;User Id = root;password = root;Database = test";

List<SensorData1> datas = new List<SensorData1>();
int length = 1000;
for (int i = 0; i < length; i++)
{
    SensorData1 model = new SensorData1();
    //model.id = i;
    model.data = new byte[1000000];
    for (int j = 0; j < model.data.Length; j++)
    {
        model.data[j] = (byte)j;
    }
    datas.Add(model);
}

int start = Environment.TickCount;
string sql = @"INSERT INTO sensor_data(data) VALUES (@data)";
using (var connection = new MySqlConnection(_conn_str))
{
    connection.Open();
    using (var tran = connection.BeginTransaction())
    {
        connection.Insert(datas);
        tran.Commit();
    }
}
int end = Environment.TickCount;
MessageBox.Show((end - start).ToString());
```
MONGODB
```CSHARP
var client = new MongoClient(conn);
var database = client.GetDatabase(dbName);
var collection = database.GetCollection<SensorData2>(tbName);

List<SensorData2> datas = new List<SensorData2>();
int length = 1000;
for (int i = 0; i < length; i++)
{
    SensorData2 model = new SensorData2();
    //model.id = i;
    model.data = new byte[1000000];
    for (int j = 0; j < model.data.Length; j++)
    {
        model.data[j] = (byte)j;
    }
    datas.Add(model);
}
int start = Environment.TickCount;
collection.InsertManyAsync(datas).ContinueWith(r=> {
    int end1 = Environment.TickCount;
    string log1 = string.Format("2.{0}->{1}", (end1 - start), collection.AsQueryable().Count());
    Console.WriteLine(log1);
});
int end = Environment.TickCount;
string log = string.Format("1.{0}->{1}", (end - start), collection.AsQueryable().Count());
Console.WriteLine(log);
//清空
var filter = Builders<SensorData2>.Filter.Empty;
var result = collection.DeleteMany(filter);
end = Environment.TickCount;
log = string.Format("3.{0}->{1}", (end - start), collection.AsQueryable().Count());
Console.WriteLine(log);
```