---
title: PYTHON笔记9 仿微信接口的XML与DICT转换
date: 2018-08-04 15:00:59
modified: 
tags: [python]
categories: python
---

&nbsp;&nbsp;这是之前使用django实现果汁机接口服务的代码,有一段XML和字典dict互转的代码非常精炼。  

![示例图片](python9/2018084.jpg)

<!--more-->

总的来说，就是XML和字典dict的相互转换
```python
# coding:utf-8
import uuid
from hashlib import md5

from bs4 import BeautifulSoup


class signhelper(object):

    def gen_sign(self, params, key):
        """
        签名生成函数

        :param params: 参数，dict 对象
        :param key: API 密钥
        :return: sign string
        """
        param_list = []
        for k in sorted(params.keys()):
            v = params.get(k)
            if not v:
                # 参数的值为空不参与签名
                continue
            param_list.append('{0}={1}'.format(k, v))
        # 在最后拼接 key
        param_list.append('key={}'.format(key))
        # 用 & 连接各 k-v 对，然后对字符串进行 MD5 运算
        return md5('&'.join(param_list).encode('utf8')).hexdigest()

    def gen_nonce_str(self):
        """
        生成随机字符串，有效字符a-zA-Z0-9

        :return: 随机字符串
        """
        return ''.join(str(uuid.uuid1()).split('-'))

    def trans_xml_to_dict(self, xml):
        """
        将微信支付交互返回的 XML 格式数据转化为 Python Dict 对象

        :param xml: 原始 XML 格式数据
        :return: dict 对象
        """

        soup = BeautifulSoup(xml, features='xml')
        xml = soup.find('xml')
        if not xml:
            return {}
        # 将 XML 数据转化为 Dict
        data = dict([(item.name, item.text) for item in xml.find_all()])
        return data


    def trans_dict_to_xml(self, data):
        """
        将 dict 对象转换成微信支付交互所需的 XML 格式数据

        :param data: dict 对象
        :return: xml 格式数据
        """

        xml = []
        for k in sorted(data.keys()):
            v = data.get(k)
            if isinstance(v ,str) and not v.startswith('<![CDATA['):
                v = '<![CDATA[{}]]>'.format(v)
            xml.append('<{key}>{value}</{key}>'.format(key=k, value=v))
        return '<xml>{}</xml>'.format(''.join(xml))
```

>P.S.  
>python对象json序列化最简单的方式
```python
s1 = json.dumps(m, default=lambda obj: obj.__dict__, sort_keys=True, indent=4)
```
>python对Json对象反序列化
```python
1.定义model
class UploadSaleModel(object):
    def __init__(self):
        super(UploadSaleModel, self).__init__()
        self.trade_no = ""
        self.sub_trade_no = ""
        self.schedule_cup = 0
        self.actual_cup_index = 0
        self.succeed_time = ""
2.编写hook的handle
def _handleUploadSaleModel(self, dic):
    try:
        model = dto.UploadSaleModel()
        model.trade_no = dic['trade_no']
        model.sub_trade_no = dic['sub_trade_no']
        model.schedule_cup = dic['schedule_cup']
        model.actual_cup_index = dic['actual_cup_index']
        model.succeed_time = dic['succeed_time']
        return model
    except Exception as ex:
        return None
3.反序列化
item = json.loads(
                input.sales, object_hook=self._handleUploadSaleModel)
```
