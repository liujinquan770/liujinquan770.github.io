---
title: dapper.net 几种数据库连接字符串
date: 2018-05-29 16:50:38
tags: [C#]
categories: C#
---

dapper.net是非常好用的ORM框架, 这里记录dapper.net常用的链接字符串.

![示例图片](csharp1/5501127.jpg)

<!--more-->

# ACCESS数据库
```
private string conn = @"Provider=Microsoft.Jet.OLEDB.4.0;Data Source=att2000.mdb";
```
P.S. ACCESS数据库内时间比较需要使用##将时间包围，如
```
using (var con = new OleDbConnection(conn))
{
    var select = string.Format(@"SELECT USERID, CHECKTIME,  CHECKTYPE, SENSORID, sn from CHECKINOUT where CHECKTIME >= #{0}# and CHECKTIME <= #{1}#",
        start_t.ToString("yyyy-MM-dd HH:mm:ss"), end_t.ToString("yyyy-MM-dd HH:mm:ss"));
    var results = con.Query<CheckInOut>(select).ToList();
    return results;
}
```

# SQLITE数据库
```
private string _conn
{
    get
    {
        //1.基础连接，FailIfMissing 参数 true=没有数据文件将异常;false=没有数据库文件则创建一个
        //Data Source=test.db;Pooling=true;FailIfMissing=false
        //2。使用utf-8 格式
        //Data Source={0};Version=3;UTF8Encoding=True;
        //3.禁用日志
        //Data Source={0};Version=3;UTF8Encoding=True;Journal Mode=Off;
        //4.连接池
        //Data Source=c:\mydb.db;Version=3;Pooling=True;Max Pool Size=100;

        return string.Format(@"Data Source={0};Pooling=true;FailIfMissing=false;Version=3;UTF8Encoding=True;Journal Mode=Off;", _dbFile);
    }
}
```

# SQLSERVER数据库
```
private string sql_conn = @"Data Source=Orange;Initial Catalog=test;User Id=sa;Password=sa;";
```

# MYSQL数据库
```
private string mysql_conn = @"server=127.0.0.1;database=test;uid=orange;pwd=123456;charset='gbk'";
```


***
# Dapper和Dapper.Contrib
参考文章 https://www.cnblogs.com/huanent/p/7762698.html  

Dapper.Contrib是对Dapper的进一步封装，使对象的基本增删改查等操作进一步简化。Dapper.Contrib不需要写sql，操作对象即可  

## entity配置
```csharp
[Table("Demo")]
public class Demo
{
    [Key] //不是自动增长主键时使用ExplicitKey
    public int Id { get; set; }

    public string Name { get; set; }

    public int Age { get; set; }

    [Computed]
    public int ComputedAge => Age * 2;

    [Write(false)]
    public int NoWriteCol { get; set; }
}
```
## 示例代码
```csharp
/// <summary>
/// 从数据库DeviceSetting读取设备参数数据并赋值到TreeDev的Device中
/// </summary>
/// <returns></returns>
public List<TreeDev.Device> GetAllDevices()
{
    List<TreeDev.Device> devices = new List<TreeDev.Device>();
    using (IDbConnection connection = new SqlConnection(_conn_str))
    {
        var result = connection.GetAll<DeviceSetting>();
        if (result != null && result.Count() > 0)
        {
            //device
            var all_device_id = result.Select(r => r.DeviceId).OrderBy(r => r).Distinct();
            foreach (var devid in all_device_id.Where(r => r.HasValue))
            {
                //todo:
            }
        }
    }
    return devices;
}

/// <summary>
/// 向数据库中插入实时数据
/// </summary>
/// <param name="rawDatas"></param>
public void WriteRawDataToDb(List<TreeDev.RawDataForDb> rawDatas)
{
    //数据转化
    var data1 = rawDatas.Select(r => new DeviceDataRaw()
    {
        RecordTime = r.recDatetime,
        DeviceId = r.DeviceId,
        DeviceName = r.dev_name,
        SensorId = r.SensorId,
        SensorName = r.sen_name,
        RawData = r.bytValue.ToArray()
    });
    //批量插入
    string sql = @"INSERT INTO DeviceDataRaw(RecordTime, DeviceId, DeviceName, SensorId, SensorName, RawData) VALUES(@RecordTime, @DeviceId, @DeviceName, @SensorId, @SensorName, @RawData)";
    using (IDbConnection connection = new SqlConnection(_conn_str))
    {
        connection.Execute(sql, data1);
    }
}
```