---
title: C#笔记10 INotifyPropertyChanged的使用
date: 2018-11-01 16:47:34
modified: 
tags: [C#]
categories: C#
---

设备采集中，有些数据变量不能一次全部获取，智能分步骤或分批次获取，或通过不同的指令获取。实际代码中我会使用类的属性记录这些数据，这些时候，我们需要监听属性值的变化，当属性值发生改变时，需要被通知。

![示例图片](csharp10/20181101.jpg)

<!--more-->

主要是参考微软的文章 https://docs.microsoft.com/zh-cn/dotnet/framework/winforms/controls/raise-change-notifications--bindingsource

# 部分经典代码
```csharp
#region 属性变更通知
public event PropertyChangedEventHandler PropertyChanged;

// This method is called by the Set accessor of each property.
// The CallerMemberName attribute that is applied to the optional propertyName
// parameter causes the property name of the caller to be substituted as an argument.
private void NotifyPropertyChanged([CallerMemberName] String propertyName = "")
{
    if (PropertyChanged != null)
    {
        PropertyChanged(this, new PropertyChangedEventArgs(propertyName));
    }
}

protected void UpdateProperty<T>(ref T properValue, T newValue, [CallerMemberName] string properName = "")
{
    if (object.Equals(properValue, newValue))
        return;

    properValue = newValue;
    NotifyPropertyChanged(properName);
}
```
属性赋值的时候可以这样使用
```csharp
public string Depth { get => _depth; private set => UpdateProperty(ref _depth, value); }
private string _depth = "";
```
相应PropertyChanged事件的时候可以使用反射的知识
```csharp
private void FoxNum1_PropertyChanged(object sender, System.ComponentModel.PropertyChangedEventArgs e)
{
    SFoxNumDataObj dataObj = new SFoxNumDataObj();
    Type t = foxNum1.GetType();
    var p = t.GetProperties().FirstOrDefault(r => r.Name == e.PropertyName);
    if (p != null)
    {
        object value = p.GetValue(foxNum1);

        if (e.PropertyName == "Depth")
        {
            dataObj.CuttingDepth = value.ToString();
        }
        else if (e.PropertyName == "CurrentLineNum")
        {
        }
        else if (e.PropertyName == "CurrentPositionX")
        {
            dataObj.XPositon = (int)value;
        }
        else if (e.PropertyName == "CurrentPositionY")
        {
            dataObj.YPositon = (int)value;
        }
        else if (e.PropertyName == "CurrentPositionZ")
        {
            dataObj.ZPositon = (int)value;
        }
        else if (e.PropertyName == "RealSpindleSpeed")
        {
            dataObj.SpindleCommandS = (uint)value;
        }
        else if (e.PropertyName == "")
        {
        }
        else if (e.PropertyName == "")
        {
        }
        else if (e.PropertyName == "")
        {
        }
    }
}
```