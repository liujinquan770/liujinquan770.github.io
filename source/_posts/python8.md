---
title: PYTHON笔记8 PYTHON操作注册表，WMI等
date: 2018-08-04 11:03:46
modified: 
tags: [python]
categories: python
---

&nbsp;&nbsp;很早以前为公司设备安装出厂软件编写的脚本，其中使用到注册表, WMI相关的知识。当时觉得很有用就记录下来了。最近整理以前的代码库，发现这段脚本，便迁移到BLOG中。  

![示例图片](python8/2018084.jpg)

<!--more-->

脚本是基于python2.7和32位操作系统，现在不一定能够运行，不过有些知识点还是很有用的。先记录下载，方便以后参考。

aeis1.py脚本
```python
# coding:utf-8
# Author:  liujinquan<120026492@qq.com>
# Purpose: 自动安装IIS5.1, .NET2.0, AEI-S1系统软件, 开启远程登录, 设置自动启动， 部署网站
# Created: 2013-04-28
import os
import sys
import time
import wmi
import _winreg
import tempfile
import shutil
import zipfile
from print_c import print_colorful


ENABLE = 1
ENABLE_CONNECTIONS = 1

# Administrator的密码
pwd = ''

# 获取脚本所在目录


def GetScriptPath():
    '''
    获取脚本所在目录
    '''
    # determine if application is a script file or frozen exe
    # 判断是EXE还是脚本文件
    application_path = None
    if getattr(sys, 'frozen', False):
        application_path = os.path.dirname(sys.executable)
    elif __file__:
        application_path = os.path.dirname(__file__)
    return application_path


def ExtracAllFromZipfile():
    print_colorful('green', True, r'正在解压文件，请稍后')
    list1 = []
    f = zipfile.ZipFile('aeis1.zip', 'u')
    list1 = f.namelist()
    # f.extractall()
    for x in list1:
        print_colorful('magenta', True, u'正在解压文件%s' % x)
        f.extract(x)
    f.close()
    print_colorful('green', True, u'解压完成')
    return list1


# 修改账户Administrator的密码为1
def ModifyPassword():
    '''
    修改账户Administrator的密码为1
    '''
    global pwd
    InputPwd()
    print_colorful(
        'green', True, r'修改Administrator的密码为%s，请记住密码' % pwd)
    command = 'net user Administrator %s' % pwd
    return os.system(command)

# 启用远程登录


def RemoteDesktop():
    '''
    启用远程登录
    '''
    global pwd
    print_colorful(
        'green', True, u'启用远程桌面功能，远程登录账户为Administrator，密码为%s' % pwd)
    c = wmi.WMI(
        moniker='winmgmts:{impersonationLevel=impersonate}//./root/cimv2')
    for a in c.Win32_Terminal():
        ret = a.Enable(ENABLE)

    for b in c.Win32_TerminalServiceSetting():
        ret = b.SetSingleSession(ENABLE)
        ret = b.SetAllowTSConnections(ENABLE_CONNECTIONS)

# 将Administrator账户设置为重启自动登录


def SetAutoLogon():
    '''
    将Administrator账户设置为重启自动登录
    '''
    global pwd
    print_colorful('green', True, u'设置Administrator为自动登录账户')
    key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,
                          u'Software\Microsoft\Windows NT\CurrentVersion\Winlogon', 0, _winreg.KEY_ALL_ACCESS)
    _winreg.SetValueEx(key, 'DefaultUserName', 0,
                       _winreg.REG_SZ, 'Administrator')
    _winreg.SetValueEx(key, 'DefaultPassword', 0, _winreg.REG_SZ, pwd)
    _winreg.SetValueEx(key, 'AutoAdminLogon', 0, _winreg.REG_SZ, '1')


# 安装IIS组件xp5.1
def InstallIIS5():
    '''
    安装IIS组件xp5.1    
    '''
    print_colorful('green', True, u'正在安装IIS 5.1组件')
    # 修改注册表，避免在安装IIS弹出'插入光盘'的提示
    key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,
                          u'Software\Microsoft\Windows\CurrentVersion\Setup', 0, _winreg.KEY_ALL_ACCESS)
    sourcepath1, type1 = _winreg.QueryValueEx(key, u'SourcePath')
    sourcepath2, type2 = _winreg.QueryValueEx(key, u'ServicePackSourcePath')
    # 将IIS安装路径设置为当前目录的i386
    iisdir = GetScriptPath()
    _winreg.SetValueEx(key, 'SourcePath', 0, _winreg.REG_SZ, iisdir)
    _winreg.SetValueEx(key, 'ServicePackSourcePath', 0, _winreg.REG_SZ, iisdir)
    sourcepath3, type1 = _winreg.QueryValueEx(key, u'SourcePath')
    sourcepath4, type2 = _winreg.QueryValueEx(key, u'ServicePackSourcePath')
    # 拷贝的临时文件夹
    shutil.copy(u'iis.txt', tempfile.gettempdir())
    # 执行IIS组件安装
    command = u'sysocmgr /i:%windir%\inf\sysoc.inf /u:%temp%\iis.txt'
    ret = os.system(command)
    # 还原注册表
    _winreg.SetValueEx(key, 'SourcePath', 0,  _winreg.REG_SZ, sourcepath1)
    _winreg.SetValueEx(key, 'ServicePackSourcePath',
                       0, _winreg.REG_SZ, sourcepath2)

# 安装.NET2框架


def InstallNetFramework():
    '''
    安装.NET2框架 
    '''
    print_colorful('green', True, u'安装.NET2.0')
    filepath = os.path.join(GetScriptPath(), u'dotnetfx2.0.exe')
    command = 'start /WAIT %s' % filepath
    ret = os.system(command)
    print_colorful('green', True, u'安装ASP.NET 2.0')
    command = u'C:\WINDOWS\Microsoft.NET\Framework\v2.0.50727\aspnet_regiis.exe -i'
    ret = os.system(command)
    return ret


def InstallPciDriver():
    filepath = os.path.join(GetScriptPath(), u'PCI卡驱动.exe')
    command = u'start /WAIT %s /SILENT ' % filepath
    ret = os.system(command)
    key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,
                          u'Software\Invengo\AEI-S1')
    pcipath, t = _winreg.QueryValueEx(key, u'PciDriverInstallPath')
    command = u'%s\wdreg.exe -inf %s\pci2040.inf install' % (pcipath, pcipath)
    ret = os.system(command)
    return ret


def InstallAeiS1():
    print_colorful('green', True, u'安装AEI-S1系统软件')
    filepath = os.path.join(GetScriptPath(), u'AEI-S1系统软件.exe')
    command = u'start /WAIT %s ' % filepath
    ret = os.system(command)
    return ret

# 设置虚拟目录


def SetVirtualDirectory():
    '''
    设置虚拟目录
    '''
    print_colorful('green', True, u'设置网站虚拟目录')
    # 取消简单共享
    command = u'reg add HKLM\SYSTEM\CurrentControlSet\Control\Lsa /v forceguest /t REG_DWORD /d 0x00000000 /f'
    ret = os.system(command)
    # 设置WEB目录的ISS账户访问权限
    #virdir = u'D:\AEI-S1\web'
    key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,
                          u'Software\Invengo\AEI-S1')
    aeipath, t = _winreg.QueryValueEx(key, u'InstallPath')
    virdir = '%s\web' % aeipath
    if not os.path.exists(virdir):
        os.makedirs(virdir)
        command = u'CACLS "%s" /C /E /G ASPNET:F' % virdir
        ret = os.system(command)
    # 设置虚拟目录
    vbsfile = os.path.join(GetScriptPath(), u'setvirtualdir.vbs')
    command = u'cscript //nologo %s' % vbsfile
    ret = os.system(command)
    return ret

# 删除临时文件


def RemoveTmpFile(list1):
    print_colorful('green', True, u'清理临时文件')
    try:
        for f in list1:
            if os.path.isdir(f):
                shutil.rmtree(f)
            elif os.path.isfile(f):
                os.remove(f)
        UninstallPkt()
    except Exception as ex:
        print(ex)

# 显示作者信息


def PrintAuthor():
    s = u'''# Author:  liujinquan<120026492@qq.com>
		Purpose: 自动安装IIS5.1, .NET2.0, AEI-S1系统软件, 开启远程登录, 设置自动启动， 部署网站
		Created: 2013-04-28'''
    print_colorful('green', True, s)

# 输入密码


def InputPwd():
    global pwd
    choose = raw_input("是否将Administrator的密码设置为 1 ? y/n?:")
    if choose == 'y' or choose == 'Y':
    	pwd = '1'
    elif choose == 'n' or choose == 'N':
    	pwd = raw_input("请输入您的密码:")
    else:
    	InputPwd()


# 卸载安装包
def UninstallPkt():
    key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,
                          u'Software\Invengo\AEI_ALL')
    aeipath, t = _winreg.QueryValueEx(key, u'InstallPath')
    unfile = r'%s\unins000.exe' % aeipath
    command = u'start /WAIT %s /VERYSILENT' % unfile
    return os.system(command)



if __name__ == "__main__":
    
    try:
        startTime = time.time()
        PrintAuthor()
        print

        print_colorful('green', True, '1')
        ModifyPassword()
        print

        print_colorful('green', True, '2')
        RemoteDesktop()
        print

        print_colorful('green', True, '3')
        SetAutoLogon()
        print

        print_colorful('green', True, '4')
        list1 = ExtracAllFromZipfile()
        print

        print_colorful('green', True, '5')
        InstallIIS5()
        print

        print_colorful('green', True, '6')
        InstallNetFramework()
        print
        # print u'安装PCI卡驱动'
        # InstallPciDriver()

        print_colorful('green', True, '7')
        InstallAeiS1()
        print

        print_colorful('green', True, '8')
        SetVirtualDirectory()
        print

        print_colorful('green', True, '9')
        RemoveTmpFile(list1)
        print

        # UninstallPkt()

        print_colorful('green', True, "使用了 %d 秒" % (time.time()-startTime))
    except Exception as ex:
        print(ex)
```