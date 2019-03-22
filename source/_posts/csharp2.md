---
title: ABP.NET的EventBus
date: 2018-06-11 15:46:02
tags: [C#]
categories: C#
---
在WEB应用项目中不可能像WINFORM随意使用Event，ABP.NET领域事件用于解耦并重复利用应用中的逻辑。

![示例图片](csharp2/20180611.jpg)

<!--more-->

参考文章(https://www.cnblogs.com/farb/p/ABPEventBus.html)

# 注入EventBus

可以直接使用 EventBus.Default，这是全局的事件总线。也可以使用依赖注入来获得IEventBus的引用，这有利于单元测试。

```
public DeviceAppService(
        IRepository<Device, Guid> deviceRepository,
        IUnitOfWorkManager unitOfWorkManager,
        Abp.Runtime.Caching.ICacheManager cacheManager
        )
    {
        EventBus = NullEventBus.Instance;

        this._cacheManager = cacheManager;
        this._unitOfWorkManager = unitOfWorkManager;
        this._deviceRepository = deviceRepository;
    }
```

# 定义事件

触发事件之前，应该先要定义该事件。事件是使用派生自EventData的类来表示的
```
public class DeviceFaultEventData : EventData
{
    public string DevCode { get; set; }
    public string DevName { get; set; }
    public string FaultCode { get; set; }
    public string FaultName { get; set; }
    public string FaultTime { get; set; }
    public string CompanyCode { get; set; }
    public string AreaCode { get; set; }
    public string FactoryCode { get; set; }

    public string Region { get; set; }
}
```

# 触发事件

```

直接调用EventBus.Trigger触发事件

EventBus.Trigger(new DeviceFaultEventData()
{
    DevCode = input.dev_code,
    DevName = device.DevName,
    FaultCode = input.fault_code,
    FaultName = faultType != null ? faultType.FaultName : "未知故障信息",
    FaultTime = input.fault_time,
    CompanyCode = !string.IsNullOrEmpty(device.CompanyCode) ? device.CompanyCode : "",
    AreaCode = !string.IsNullOrEmpty(device.AreaShow) ? device.AreaShow : "",
    Region = !string.IsNullOrEmpty(device.Region) ? device.Region : "",
    FactoryCode = !string.IsNullOrEmpty(device.FactoryCode) ? device.FactoryCode : "",
});
```

# 处理事件

要处理一个事件，应该要实现IEventHandler接口
```
public class EventBusHandler : ITransientDependency,
        IEventHandler<DeviceFaultEventData>,
        IEventHandler<PaymentNotifyEventData>
    {
        private string jpush_appkey = ConfigurationManager.AppSettings["JPushAppKey"];
        private string jpush_secret = ConfigurationManager.AppSettings["JPushSecret"];
        private string jpush_tenant_role = ConfigurationManager.AppSettings["JPushTenantRole"];
        private string jpush_appkey_wh = ConfigurationManager.AppSettings["JPushAppKeyWh"];
        private string jpush_secret_wh = ConfigurationManager.AppSettings["JPushSecretWh"];
        private string jpush_staff_role = ConfigurationManager.AppSettings["JPushStaffRole"];
        private string jpush_400service_role = ConfigurationManager.AppSettings["JPush400ServiceRole"];
        private string jpush_whsc_role = ConfigurationManager.AppSettings["JPushWhScRole"];

        public void HandleEvent(PaymentNotifyEventData eventData)
        {
            //Console.WriteLine(eventData.OutTradeNo + ":" + eventData.PayResult);
            //todo:
            //这里可以推送支付成功的消息推送出去
        }

        /// <summary>
        /// 设备故障的事件, 采用极光推送
        /// </summary>
        /// <param name="eventData"></param>
        public void HandleEvent(DeviceFaultEventData eventData)
        {
            string dev_code = eventData.DevCode;
            string dev_name = eventData.DevName;
            string fault_code = eventData.FaultCode;
            string fault_name = eventData.FaultName;
            string fault_time = eventData.FaultTime;
            string company_code = eventData.CompanyCode;
            string area_code = eventData.AreaCode.Replace("/", "");
            string facotry_code = eventData.FactoryCode;
            string region = eventData.Region;

            Abp.Logging.LogHelper.Logger.Info(string.Format("收到设备故障的事件. {0}", JsonConvert.SerializeObject(eventData)));

            if (Constants.DEVICE_FAULT_FRUIT_NOT_ENOUGH.Keys.Contains(fault_code))
            {
                //橙子不足
                if ((!string.IsNullOrEmpty(company_code)) && (!string.IsNullOrEmpty(jpush_tenant_role)))
                {
                    string tag = string.Format("{0}_{1}", company_code, jpush_tenant_role);
                    Dictionary<string, List<string>> tags = new Dictionary<string, List<string>>();
                    tags["tag"] = new List<string> { tag };

                    //编号为QFBOTAL10008的设备，橙子储量不足，发生时间：18 - 05 - 10 17:14:03
                    //编号为QFBOTAL10008的设备，橙子储量不足停止榨汁，发生时间：18 - 05 - 10 17:14:03
                    string title = !string.IsNullOrEmpty(fault_name) ? fault_name : Constants.DEVICE_FAULT_FRUIT_NOT_ENOUGH[fault_code];
                    string content = string.Format("编号为{0}的设备, {1}, 发生时间: {2}", facotry_code, title, fault_time);

                    Dictionary<string, object> extras = new Dictionary<string, object>();
                    extras["dev_code"] = dev_code;
                    extras["dev_name"] = dev_name;
                    extras["fault_code"] = fault_code;
                    extras["fault_time"] = fault_time;
                    extras["factory_code"] = facotry_code;
                    JiGuangPush.PushNotification(jpush_appkey, jpush_secret, tags, title, content, extras);

                    string log = string.Format("推送橙子不足的消息到送橙人员. tags is {0}, title is {1}, content is {2}, extras is {3}",
                                            JsonConvert.SerializeObject(tags), title, content, JsonConvert.SerializeObject(extras));
                    Abp.Logging.LogHelper.Logger.Info(log);
                }
            }
            else if (Constants.DEVICE_FAULT_PAYED_BUT_NO_JUICER.Keys.Contains(fault_code))
            {
                //付费未榨汁
                if (!string.IsNullOrEmpty(jpush_400service_role))
                {
                    string tag = jpush_400service_role;
                    Dictionary<string, List<string>> tags = new Dictionary<string, List<string>>();
                    tags["tag"] = new List<string> { tag };

                    string title = fault_name;
                    string content = string.Format("编号为{0}的设备, 出现已支付未出杯的情况, 发生时间: {1}", facotry_code, fault_time);
                    Dictionary<string, object> extras = new Dictionary<string, object>();
                    extras["dev_code"] = dev_code;
                    extras["fault_code"] = fault_code;
                    extras["fault_time"] = fault_time;
                    extras["factory_code"] = facotry_code;
                    JiGuangPush.PushNotification(jpush_appkey_wh, jpush_secret_wh, tags, title, content, extras);

                    string log = string.Format("推送付费未榨汁的消息到400维护人员. tags is {0}, title is {1}, content is {2}, extras is {3}",
                                            JsonConvert.SerializeObject(tags), title, content, JsonConvert.SerializeObject(extras));
                    Abp.Logging.LogHelper.Logger.Info(log);
                }
            }
            else
            {
                //TODO:其他故障按区域推送到维护人员
                if ((!string.IsNullOrEmpty(region)) && (!string.IsNullOrEmpty(jpush_staff_role)))
                {
                    string tag = string.Format("{0}_{1}", region, jpush_staff_role);
                    Dictionary<string, List<string>> tags = new Dictionary<string, List<string>>();
                    tags["tag"] = new List<string> { tag };

                    //编号为QFBOTAL10008的设备发生故障，故障代码为:0x03，故障发生时间：18-05-10 17:14:03
                    string title = fault_name;
                    string content = string.Format("编号为{0}的设备发生故障, 故障代码为: 0x{1}, 故障发生时间: {2}", facotry_code, fault_code, fault_time);
                    Dictionary<string, object> extras = new Dictionary<string, object>();
                    extras["dev_code"] = dev_code;
                    extras["fault_code"] = fault_code;
                    extras["fault_time"] = fault_time;
                    extras["region"] = region;
                    extras["factory_code"] = facotry_code;
                    JiGuangPush.PushNotification(jpush_appkey_wh, jpush_secret_wh, tags, title, content, extras);

                    string log = string.Format("推送设备故障消息到维护人员. tags is {0}, title is {1}, content is {2}, extras is {3}",
                                            JsonConvert.SerializeObject(tags), title, content, JsonConvert.SerializeObject(extras));
                    Abp.Logging.LogHelper.Logger.Info(log);
                }
            }

            //维护兼送橙人员可以收到所有故障通知
            if (!string.IsNullOrEmpty(jpush_whsc_role))
            {
                string tag = string.Format("{0}", jpush_whsc_role);
                Dictionary<string, List<string>> tags = new Dictionary<string, List<string>>();
                tags["tag"] = new List<string> { tag };

                string title = fault_name;
                string content = string.Format("编号为{0}的设备发生故障, 故障代码为: 0x{1}, 故障发生时间: {2}", facotry_code, fault_code, fault_time);
                Dictionary<string, object> extras = new Dictionary<string, object>();
                extras["dev_code"] = dev_code;
                extras["fault_code"] = fault_code;
                extras["fault_time"] = fault_time;
                extras["region"] = region;
                extras["factory_code"] = facotry_code;
                JiGuangPush.PushNotification(jpush_appkey_wh, jpush_secret_wh, tags, title, content, extras);
                JiGuangPush.PushNotification(jpush_appkey, jpush_secret, tags, title, content, extras);

                string log = string.Format("推送设备故障消息到维护兼送橙人员. tags is {0}, title is {1}, content is {2}, extras is {3}",
                                            JsonConvert.SerializeObject(tags), title, content, JsonConvert.SerializeObject(extras));
                Abp.Logging.LogHelper.Logger.Info(log);
            }
        }
    }
```

>在WEB开发中，常用发送邮件，或推送等耗时的操作，可通过EventBus将其从核心服务代码中分离出来。