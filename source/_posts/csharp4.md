---
title: C#笔记4 KAFKA安装和调用
date: 2018-08-20 10:19:10
modified: 
tags: [C#]
categories: C#
---

记录Kafka在windows7x64环境下安装和调用过程。  

![示例图片](csharp4/20180820.jpg)

<!--more-->

## 安装
安装过程参考文章https://www.cnblogs.com/flower1990/p/7466882.html,一次成功

## C#调用示例代码
使用的SDK可以从https://github.com/confluentinc/confluent-kafka-dotnet下载，或nuget获取包
生产者代码
```csharp
var config = new Dictionary<string, object>
{
    { "bootstrap.servers", "localhost:9092" }
};

using (var producer = new Producer<Null, string>(config, null, new StringSerializer(Encoding.UTF8)))
{
    var dr = producer.ProduceAsync("test", null, "test message text").Result;
    Console.WriteLine($"Delivered '{dr.Value}' to: {dr.TopicPartitionOffset}");
}
```
消费者代码
```csharp
var conf = new Dictionary<string, object>
{
    { "group.id", "test-consumer-group" },
    { "bootstrap.servers", "localhost:9092" },
    { "auto.commit.interval.ms", 5000 },
    { "auto.offset.reset", "earliest" }
};

using (var consumer = new Consumer<Null, string>(conf, null, new StringDeserializer(Encoding.UTF8)))
{
    consumer.OnMessage += (_, msg)
        => Console.WriteLine($"Read '{msg.Value}' from: {msg.TopicPartitionOffset}");

    consumer.OnError += (_, error)
        => Console.WriteLine($"Error: {error}");

    consumer.OnConsumeError += (_, msg)
        => Console.WriteLine($"Consume error ({msg.TopicPartitionOffset}): {msg.Error}");

    consumer.Subscribe("test");

    while (true)
    {
        consumer.Poll(TimeSpan.FromMilliseconds(100));
    }
}
```

## PYTHON示例代码
生产者
```python
import time

from kafka import KafkaProducer

producer = KafkaProducer(bootstrap_servers=['127.0.0.1:9092'])

topic = 'test'


def test():
    print('begin')
    for n in range(1, 100):
        s = '{0}'.format(n)
        producer.send(topic, bytes(s,encoding='utf8'))
        print('send {0}'.format(str(n)))
        time.sleep(0.5)
    print('done')

if __name__ == '__main__':
    test()
    producer.close()
```
消费者
```python
from kafka import KafkaConsumer

consumer = KafkaConsumer('test',
                         bootstrap_servers=['127.0.0.1:9092'])
                         
for message in consumer:
    print("%s:%d:%d: key=%s value=%s".format(message.topic, message.partition,
                                          message.offset, message.key,
                                          message.value))
```

## AVRO的序列化和反序列化
引入Confluent.Kafka.Avro
```csharp
private byte[] SerializeFromSpecial<T>(T t) where T : ISpecificRecord
{
    //ByteBufferOutputStream比MemoryStream有優化,最後的字節少很多
    ByteBufferOutputStream stream = new ByteBufferOutputStream();
    Avro.IO.Encoder encoder = new BinaryEncoder(stream);
    var writer = new SpecificDatumWriter<T>(t.Schema);
    writer.Write(t, encoder);
    stream.Flush();

    var bufferArray = stream.GetBufferList().SelectMany(r => r.ToArray()).ToArray();
    return bufferArray;
}

private T DeseializeToSpecial<T>(byte[] data) where T : ISpecificRecord
{
    //T t = default(T);
    T t = System.Activator.CreateInstance<T>();
    var reader = new SpecificDatumReader<T>(t.Schema, t.Schema);
    Stream stream = new MemoryStream(data);
    var decoder = new BinaryDecoder(stream);
    var result = reader.Read(t, decoder);
    stream.Flush();

    return result;
}
```
[avro-gen工具](avrogen.zip)  

## AVRO的序列化和反序列化(python)
引入kafka-python和fastavro
```python
import json
from io import BytesIO

import fastavro
from kafka import KafkaConsumer

# 序列化和反序列化
def avro_to_bytes_with_schema(avro_schema, avro_dict):
    with BytesIO() as bytes_io:
        fastavro.writer(bytes_io, avro_schema, [avro_dict])
        return bytes_io.getvalue()


def bytes_with_schema_to_avro(avro_read_schema, binary):
    with BytesIO(binary) as bytes_io:
        reader = fastavro.schemaless_reader(bytes_io, avro_read_schema)
        return reader


CONSUMER = KafkaConsumer(
    'acce6', group_id='acce_group121', bootstrap_servers=['192.168.1.41:9092'])

SCHEMA_PATH = 'sensor.avsc'
new_schema = json.loads(open(SCHEMA_PATH, 'r').read())

for msg in CONSUMER:
    data = bytes_with_schema_to_avro(old_schema, msg.value)
    print(data)

```
avsc文件
```json
{
  "namespace": "com.esgyn.foxconnAI.avro",
  "type": "record",
  "name": "Sensor",
  "fields": [
    {
      "name": "device_id",
      "type": "string"
    },
    {
      "name": "sample_ts",
      "type": "long"
    },
    {
      "name": "sensor_id",
      "type": "string"
    },
    {
      "name": "data",
      "type": {
        "type": "array",
        "items": "double"
      }
    },
    {
      "name": "input_speed",
      "type": [
        "null",
        "string"
      ]
    },
    {
      "name": "spindle_speed",
      "type": [
        "null",
        "string"
      ]
    },
    {
      "name": "feed_rate",
      "type": [
        "null",
        "string"
      ]
    },
    {
      "name": "spindle_load_ratio",
      "type": [
        "null",
        "string"
      ]
    },
    {
      "name": "spindle_current",
      "type": [
        "null",
        "string"
      ]
    },
    {
      "name": "motor_temperature",
      "type": [
        "null",
        "string"
      ]
    },
    {
      "name": "cutting_depth",
      "type": [
        "null",
        "string"
      ]
    },
    {
      "name": "cutting_time",
      "type": [
        "null",
        "string"
      ]
    },
    {
      "name": "booting_time",
      "type": [
        "null",
        "string"
      ]
    },
    {
      "name": "operating_time",
      "type": [
        "null",
        "string"
      ]
    },
    {
      "name": "x_axis_position",
      "type": [
        "null",
        "string"
      ]
    },
    {
      "name": "y_axis_position",
      "type": [
        "null",
        "string"
      ]
    },
    {
      "name": "z_axis_position",
      "type": [
        "null",
        "string"
      ]
    }
  ]
}
```

## avro嵌套的schema示例
```json
{
  "namespace": "foxconn.smarttool.avro",
  "name": "HncData",
  "type": "record",
  "fields": [
    {
      "name": "record_time",
      "type": "long"
    },
    {
      "name": "axis_data",
      "type": {
        "type": "array",
        "items": {
          "type": "record",
          "name": "AxisVals",
          "fields": [
            {
              "name": "name",
              "type": "string"
            },
            {
              "name": "load_current",
              "type": "double"
            },
            {
              "name": "motor_rev",
              "type": "double"
            },
            {
              "name": "rel_zero",
              "type": "double"
            },
            {
              "name": "z_dist",
              "type": "double"
            },
            {
              "name": "comp_val",
              "type": "double"
            },
            {
              "name": "syn_err",
              "type": "double"
            },
            {
              "name": "follow_err",
              "type": "double"
            },
            {
              "name": "wheel_off",
              "type": "double"
            },
            {
              "name": "wcs_zero",
              "type": "double"
            },
            {
              "name": "left_to_go",
              "type": "double"
            },
            {
              "name": "act_vel",
              "type": "double"
            },
            {
              "name": "cmd_vel",
              "type": "double"
            },
            {
              "name": "prog_pos",
              "type": "double"
            },
            {
              "name": "cmd_rcs_pos",
              "type": "double"
            },
            {
              "name": "act_rcs_pos",
              "type": "double"
            },
            {
              "name": "cmd_wcs_pos",
              "type": "double"
            },
            {
              "name": "act_wcs_pos",
              "type": "double"
            },
            {
              "name": "sv_ver",
              "type": "string"
            },
            {
              "name": "sv_type",
              "type": "string"
            },
            {
              "name": "type",
              "type": "int"
            },
            {
              "name": "chan_no",
              "type": "int"
            },
            {
              "name": "ch_axis_no",
              "type": "int"
            },
            {
              "name": "lead_axis_no",
              "type": "int"
            },
            {
              "name": "rated_current",
              "type": "double"
            },
            {
              "name": "act_pulse",
              "type": "int"
            },
            {
              "name": "enc_cntr",
              "type": "int"
            },
            {
              "name": "is_homed",
              "type": "int"
            },
            {
              "name": "z_space1",
              "type": "int"
            },
            {
              "name": "z_space2",
              "type": "int"
            },
            {
              "name": "act_pos",
              "type": "double"
            },
            {
              "name": "cmd_pos",
              "type": "double"
            },
            {
              "name": "cmd_pulse",
              "type": "int"
            },
            {
              "name": "wave_freq",
              "type": "double"
            }
          ]
        }
      }
    },
    {
      "name": "chan_data",
      "type": {
        "type": "array",
        "items": {
          "type": "record",
          "name": "ChanVals",
          "fields": [
            {
              "name": "name",
              "type": "string"
            },
            {
              "name": "is_homing",
              "type": "int"
            },
            {
              "name": "is_moving",
              "type": "int"
            },
            {
              "name": "diameter",
              "type": "int"
            },
            {
              "name": "is_verify",
              "type": "int"
            },
            {
              "name": "run_row",
              "type": "int"
            },
            {
              "name": "dcd_row",
              "type": "int"
            },
            {
              "name": "sel_prog",
              "type": "int"
            },
            {
              "name": "run_prog",
              "type": "int"
            },
            {
              "name": "part_cntr",
              "type": "int"
            },
            {
              "name": "part_total_num",
              "type": "int"
            },
            {
              "name": "h_off",
              "type": "int"
            },
            {
              "name": "d_off",
              "type": "int"
            },
            {
              "name": "prog_name",
              "type": "bytes"
            },
            {
              "name": "chan_lax",
              "type": {
                "type": "array",
                "items": "int"
              }
            },
            {
              "name": "chan_axis_name",
              "type": {
                "type": "array",
                "items": "string"
              }
            },
            {
              "name": "chan_spdl_name",
              "type": {
                "type": "array",
                "items": "string"
              }
            },
            {
              "name": "chan_modal",
              "type": {
                "type": "array",
                "items": "int"
              }
            },
            {
              "name": "chan_spdl_lax",
              "type": {
                "type": "array",
                "items": "int"
              }
            },
            {
              "name": "chan_spdl_para_lax",
              "type": {
                "type": "array",
                "items": "int"
              }
            },
            {
              "name": "cmd_spdl_speed",
              "type": {
                "type": "array",
                "items": "double"
              }
            },
            {
              "name": "act_spdl_speed",
              "type": {
                "type": "array",
                "items": "double"
              }
            },
            {
              "name": "is_running",
              "type": "int"
            },
            {
              "name": "is_reseting",
              "type": "int"
            },
            {
              "name": "is_estop",
              "type": "int"
            },
            {
              "name": "is_rewinded",
              "type": "int"
            },
            {
              "name": "mac_type",
              "type": "int"
            },
            {
              "name": "axes_mask",
              "type": "int"
            },
            {
              "name": "axes_mask1",
              "type": "int"
            },
            {
              "name": "cmd_type",
              "type": "int"
            },
            {
              "name": "cmd_feed_rate",
              "type": "double"
            },
            {
              "name": "act_feed_rate",
              "type": "double"
            },
            {
              "name": "prog_feed_rate",
              "type": "double"
            },
            {
              "name": "feed_override",
              "type": "int"
            },
            {
              "name": "rapid_override",
              "type": "int"
            },
            {
              "name": "mcode",
              "type": "int"
            },
            {
              "name": "spdl_override",
              "type": {
                "type": "array",
                "items": "int"
              }
            },
            {
              "name": "tcode",
              "type": "int"
            },
            {
              "name": "tool_use",
              "type": "int"
            },
            {
              "name": "tool_rdy",
              "type": "int"
            },
            {
              "name": "chan_mode",
              "type": "int"
            },
            {
              "name": "is_mdi",
              "type": "int"
            },
            {
              "name": "is_cycle",
              "type": "int"
            },
            {
              "name": "is_hold",
              "type": "int"
            },
            {
              "name": "is_prog_sel",
              "type": "int"
            },
            {
              "name": "is_prog_end",
              "type": "int"
            },
            {
              "name": "is_threading",
              "type": "int"
            },
            {
              "name": "is_rigid",
              "type": "int"
            },
            {
              "name": "t_offs",
              "type": "int"
            },
            {
              "name": "bp_pos",
              "type": {
                "type": "array",
                "items": "double"
              }
            }
          ]
        }
      }
    },
    {
      "name": "alarm_data",
      "type": {
        "type": "array",
        "items": {
          "type": "record",
          "name": "AlarmData",
          "fields": [
            {
              "name": "alarm_no",
              "type": "int"
            },
            {
              "name": "alarm_text",
              "type": "string"
            }
          ]
        }
      }
    },
    {
      "name": "sys_data",
      "type": {
        "type": "record",
        "name": "SysData",
        "fields": [
          {
            "name": "chan_num",
            "type": "int"
          },
          {
            "name": "move_unit",
            "type": "int"
          },
          {
            "name": "turn_unit",
            "type": "int"
          },
          {
            "name": "metric_disp",
            "type": "int"
          },
          {
            "name": "show_time",
            "type": "int"
          },
          {
            "name": "pop_alarm",
            "type": "int"
          },
          {
            "name": "graph_erase",
            "type": "int"
          },
          {
            "name": "mac_type",
            "type": "int"
          },
          {
            "name": "prec",
            "type": "int"
          },
          {
            "name": "f_prec",
            "type": "int"
          },
          {
            "name": "s_prec",
            "type": "int"
          },
          {
            "name": "cnc_ver",
            "type": "int"
          },
          {
            "name": "mcp_key",
            "type": "int"
          },
          {
            "name": "active_chan",
            "type": "int"
          },
          {
            "name": "request_chan",
            "type": "int"
          },
          {
            "name": "mdi_chan",
            "type": "int"
          },
          {
            "name": "request_chan_mask",
            "type": "int"
          },
          {
            "name": "is_hold_redecode",
            "type": "int"
          },
          {
            "name": "access_level",
            "type": "int"
          },
          {
            "name": "rights_key",
            "type": "int"
          },
          {
            "name": "reg_days_remaining",
            "type": "int"
          },
          {
            "name": "nck_ver",
            "type": "string"
          },
          {
            "name": "drv_ver",
            "type": "string"
          },
          {
            "name": "plc_ver",
            "type": "string"
          },
          {
            "name": "nc_ver",
            "type": "string"
          },
          {
            "name": "sn_num",
            "type": "string"
          },
          {
            "name": "machine_type",
            "type": "string"
          },
          {
            "name": "machine_info",
            "type": "string"
          },
          {
            "name": "mac_fac_info",
            "type": "string"
          },
          {
            "name": "user_info",
            "type": "string"
          },
          {
            "name": "machine_num",
            "type": "string"
          },
          {
            "name": "ex_factory_date",
            "type": "string"
          }
        ]
      }
    }
  ]
}
```
