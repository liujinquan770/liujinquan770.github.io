---
title: C#笔记13 C#中知识点记录
date: 2019-07-24 10:59:06
modified: 
tags: [C#]
categories: C#
---

该文档主要是记录一些c#开发中比较零碎的小知识点。

![示例图片](csharp13/4038001.jpg)

<!--more-->

## WINFORM 的皮肤控件
用IrisSkin轻松实现换肤功能。  
[DLL](IrisSkin4.zip)   
[皮肤](skin60.zip)  
示例代码如下
```csharp
this.skinEngine1 = new Sunisoft.IrisSkin.SkinEngine(((System.ComponentModel.Component)(this)));
        this.skinEngine1.SkinAllForm = true;
        this.skinEngine1.SkinFile = Path.Combine(Application.StartupPath, "Skins", AppConfig.SkinFileName);
```

## WINFORM 调用VLC播放视频器控件
引入nuget包
```xml
<package id="Vlc.DotNet.Core" version="3.0.0" targetFramework="net472" />
<package id="Vlc.DotNet.Core.Interops" version="3.0.0" targetFramework="net472" />
<package id="Vlc.DotNet.Forms" version="3.0.0" targetFramework="net472" />
```
具体使用过程可参考  
https://github.com/ZeBobo5/Vlc.DotNet  

需要注意的观察编译后是否有生成libvlc文件夹如果没有,可以从上面url下载示例代码编译后再拷贝。

部分示例代码
```csharp
private void vlcControl1_VlcLibDirectoryNeeded(object sender, Vlc.DotNet.Forms.VlcLibDirectoryNeededEventArgs e)
{
    var currentDirectory = Path.GetDirectoryName(Assembly.GetEntryAssembly().Location);
    var libDirectory =
        new DirectoryInfo(Path.Combine(currentDirectory, "libvlc", IntPtr.Size == 4 ? "win-x86" : "win-x64"));
    e.VlcLibDirectory = libDirectory;
    //vlcControl1.VlcMediaplayerOptions = new[] { "--repeat" };
}

private void FrmMainMDI2_Load(object sender, EventArgs e)
{
    vlcControl1.VlcMediaPlayer.SetMedia(new Uri(@"E:\2\video_01.mp4"));
    vlcControl1.VlcMediaPlayer.Play();
}

private void vlcControl1_SizeChanged(object sender, EventArgs e)
{
    vlcControl1.VlcMediaPlayer.SetMedia(new Uri(@"E:\2\video_01.mp4"));
    vlcControl1.VlcMediaPlayer.Play();
}

private void vlcControl1_Stopped(object sender, Vlc.DotNet.Core.VlcMediaPlayerStoppedEventArgs e)
{
}

private void vlcControl1_EndReached(object sender, Vlc.DotNet.Core.VlcMediaPlayerEndReachedEventArgs e)
{
    // 循环播放必须新开线程
    //Task.Factory.StartNew(()=> {
    //    vlcControl1.VlcMediaPlayer.Stop();
    //    vlcControl1.VlcMediaPlayer.SetMedia(new Uri(@"E:\2\video_01.mp4"));
    //    vlcControl1.VlcMediaPlayer.Play();
    //}, TaskCreationOptions.AttachedToParent);
    
}

private void btnRun_Click(object sender, EventArgs e)
{
    vlcControl1.VlcMediaPlayer.Stop();
    vlcControl1.VlcMediaPlayer.SetMedia(new Uri(@"E:\2\video_01.mp4"));
    vlcControl1.VlcMediaPlayer.Play();
}
```

## C#使用SSH.NET向LINUX传输文件
引入nuget包
```xml
<package id="SSH.NET" version="2016.1.0" targetFramework="net46" />
```

代码
```csharp
public class SSHHelper
{
    private SftpClient sftpClient = null;
    public bool Connect(string host, string username, string password)
    {
        try
        {
            if (sftpClient != null)
            {
                sftpClient.Disconnect();
                sftpClient.Dispose();
            }

            sftpClient = new SftpClient(host, username, password);
            sftpClient.KeepAliveInterval = TimeSpan.FromSeconds(30);
            sftpClient.Connect();

            return sftpClient.IsConnected;
        }
        catch (Exception ex)
        {
            sftpClient = null;
            return false;
        }
    }
    /// <summary>
    /// SFTP上传文件
    /// </summary>
    /// <param name="host"></param>
    /// <param name="username"></param>
    /// <param name="password"></param>
    /// <param name="local_path">本地文件 </param>
    /// <param name="remote_path">远程文件,最好是全路径</param>
    public void UploadFile(string local_path, string remote_base, string remote_sub, string remote_filename, bool remove_local = true)
    {
        try
        {
            if (sftpClient == null)
                return;
            if (!sftpClient.IsConnected)
                return;

            sftpClient.ChangeDirectory(remote_base);
            var sub_folders = remote_sub.Split(new char[] { Path.DirectorySeparatorChar }, StringSplitOptions.RemoveEmptyEntries);
            foreach (var d in sub_folders)
            {
                if (!sftpClient.Exists(d))
                    sftpClient.CreateDirectory(d);
                sftpClient.ChangeDirectory(d);
            }
            sftpClient.UploadFile(
                File.Open(local_path, FileMode.Open, FileAccess.Read, FileShare.Delete), //FileShare.Delete允许后续可以删除这个文件(而不是删除时候抛出异常)
                remote_filename,
                new Action<ulong>((e) =>
                {
                    string log = string.Format("file:{0}->{1}", remote_filename, e);
                    Console.WriteLine(log);
                })
            );

            if (remove_local)
            {
                File.Delete(local_path);
            }
        }
        catch (Exception ex)
        {
            Logger.WriteExceptionLog(ex);
        }
    }

    /// <summary>
    /// 下载文件
    /// </summary>
    /// <param name="host"></param>
    /// <param name="username"></param>
    /// <param name="password"></param>
    /// <param name="local_path"></param>
    /// <param name="remote_path"></param>
    public void DownloadFile(string local_path, string remote_path)
    {
        try
        {
            if (sftpClient == null)
                return;
            if (!sftpClient.IsConnected)
                return;

            var folder = Path.GetDirectoryName(local_path);
            if (!Directory.Exists(folder))
                Directory.CreateDirectory(folder);
            sftpClient.DownloadFile(remote_path, File.Open(local_path, FileMode.OpenOrCreate));
        }
        catch (Exception ex)
        {
            Logger.WriteExceptionLog(ex);
        }
    }
}
```
