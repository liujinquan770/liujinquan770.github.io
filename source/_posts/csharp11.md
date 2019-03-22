---
title: C#笔记11 MsChart简单使用
date: 2019-01-07 19:56:47
modified: 
tags: [C#]
categories: C#
---

winform中自带的mschart类似百度的echarts, 效果其实也不错，特别是折线图用来显示采集数据的是时域图和频域图是非常的方便。

![示例图片](csharp11/2019017.jpg)

<!--more-->

废话不多说，贴代码。

设置样式
```csharp
//设置Series样式
private Series SetSeriesStyle(Color color, string serie_name = "1")
{
    Series series = new Series(serie_name);

    //Series的类型
    series.ChartType = SeriesChartType.Line;
    //Series的边框颜色
    series.BorderColor = Color.FromArgb(180, 26, 59, 105);
    //线条宽度
    series.BorderWidth = 1;
    //线条阴影颜色
    //series.ShadowColor = Color.Black;
    //阴影宽度
    //series.ShadowOffset = 2;
    //是否显示数据说明
    series.IsVisibleInLegend = true;
    //线条上数据点上是否有数据显示
    series.IsValueShownAsLabel = false;
    //线条上的数据点标志类型
    series.MarkerStyle = MarkerStyle.None;
    //线条数据点的大小
    series.MarkerSize = 1;
    //线条颜色
    series.Color = color;// Color.FromArgb(220, 65, 140, 240);
    return series;
}

/// <summary>
/// 初始化Char控件样式
/// </summary>
public void InitializeChart(Chart myChart, string titleChart, double max = System.Double.NaN, double min = System.Double.NaN)
{
    #region 设置图表的属性

    //图表的背景色
    myChart.BackColor = Color.FromArgb(211, 223, 240);
    //图表背景色的渐变方式
    //myChart.BackGradientStyle = GradientStyle.TopBottom;
    //图表的边框颜色、
    myChart.BorderlineColor = Color.FromArgb(26, 59, 105);
    //图表的边框线条样式
    myChart.BorderlineDashStyle = ChartDashStyle.Solid;
    //图表边框线条的宽度
    myChart.BorderlineWidth = 2;
    //图表边框的皮肤
    myChart.BorderSkin.SkinStyle = BorderSkinStyle.Emboss;

    #endregion 设置图表的属性

    #region 设置图表的Title

    Title title = new Title();
    //标题内容
    title.Text = titleChart;
    //标题的字体
    title.Font = new System.Drawing.Font("Microsoft Sans Serif", 12, FontStyle.Bold);
    //标题字体颜色
    title.ForeColor = Color.FromArgb(26, 59, 105);
    //标题阴影颜色
    title.ShadowColor = Color.FromArgb(32, 0, 0, 0);
    //标题阴影偏移量
    title.ShadowOffset = 3;

    myChart.Titles.Add(title);

    #endregion 设置图表的Title

    #region 设置图表区属性

    //图表区的名字
    ChartArea chartArea = new ChartArea("Default");
    ////背景色
    chartArea.BackColor = Color.White;// Color.FromArgb(64, 165, 191, 228);
    //背景渐变方式
    //chartArea.BackGradientStyle = GradientStyle.TopBottom;
    //渐变和阴影的辅助背景色
    //chartArea.BackSecondaryColor = Color.White;
    //边框颜色
    chartArea.BorderColor = Color.FromArgb(64, 64, 64, 64);
    //阴影颜色
    chartArea.ShadowColor = Color.Transparent;

    //设置X轴和Y轴线条的颜色和宽度

    chartArea.AxisX.LineColor = Color.FromArgb(64, 64, 64, 64);
    chartArea.AxisX.LineWidth = 1;
    chartArea.AxisY.LineColor = Color.FromArgb(64, 64, 64, 64);
    chartArea.AxisY.LineWidth = 1;
    chartArea.AxisY.Maximum = max;
    chartArea.AxisY.Minimum = min;

    //设置X轴和Y轴的标题
    //chartArea.AxisX.Title = "横坐标标题";
    //chartArea.AxisY.Title = "纵坐标标题";

    //设置图表区网格横纵线条的颜色和宽度
    chartArea.AxisX.MajorGrid.Enabled = false;
    chartArea.AxisY.MajorGrid.Enabled = false;
    chartArea.AxisX.MajorGrid.LineColor = Color.FromArgb(64, 64, 64, 64);
    chartArea.AxisX.MajorGrid.LineWidth = 1;
    chartArea.AxisY.MajorGrid.LineColor = Color.FromArgb(64, 64, 64, 64);
    chartArea.AxisY.MajorGrid.LineWidth = 1;

    myChart.ChartAreas.Add(chartArea);
    myChart.ChartAreas.RemoveAt(0);

    #endregion 设置图表区属性

    #region 图例及图例的位置

    //Legend legend = new Legend();
    //legend.Alignment = StringAlignment.Center;
    //legend.Docking = Docking.Bottom;

    //myChart.Legends.Add(legend);
    //myChart.Legends.Clear();

    #endregion 图例及图例的位置
}
```
填充数据
```csharp
private void RefreshDataForSensor(float[] xdata, float[] ydata, Chart chart)
{
    chart.BeginInvoke(new Action(() =>
    {
        try
        {
            chart.Series.Clear();
            Series series = this.SetSeriesStyle(Color.Red, "acc");
            for (int i = 0; i < xdata.Length; i++)
            {
                series.Points.AddXY(xdata[i], ydata[i]);
            }
            chart.Series.Add(series);
        }
        catch (Exception)
        {
        }
    }));
    //Application.DoEvents();
}
```
