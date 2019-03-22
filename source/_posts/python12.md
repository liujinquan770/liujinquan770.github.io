---
title: PYTHON笔记12 PYQT入门步骤
date: 2018-09-02 14:43:46
modified: 
tags: [python]
categories: python
---

使用PYQT5和VSCODE编写最简单的窗口程序。

![示例图片](python12/2018092.jpg)

<!--more-->

VSCODE对PYQT的智能提示和import引入功能不够强大，所以只适合编写简单的PYQT程序.专业的还是需要安装PyCharm。

## 安装依赖包
```python
pip install pyqt5 pyqt5-tools
```
并且vscode安装插件PYQT Integration。首次使用需要配置pyrcc5.exe的路径

## 使用pyqt-tools的编辑窗口
在vscode的左侧"资源管理器"点击右键，出现菜单"PYQT:New Form"出现一个编辑窗口，可自定拖拉控件编辑窗口布局。  
编辑完毕后保存关闭，然后在vscode执行"PYQT:Compile Form".  
假设得到的是dlg_main.ui和Ui_dlg_main.py。这两个是窗口布局文件。我们还需要自己编写代码细化该窗口的功能。  
新建"Handler_dlg_main.py".代码如下
```python
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QDialog, QMessageBox
from Ui_dlg_main import Ui_DlgMain


class Handler_DlgMain(QDialog):
    def __init__(self, parent=None):
        super(Handler_DlgMain, self).__init__(parent)
        self.ui = Ui_DlgMain()
        self.ui.setupUi(self)
        self.ui.btn1.clicked.connect(self.slotLogin)

    def slotLogin(self):
        button = QMessageBox.question(self, "Question", "检测到程序有更新，是否安装最新版本？",
                                      QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Ok)

        if button == QMessageBox.Ok:
            self.ui.resultLabel.setText(
                "<h2>Question:<font color=red>  OK</font></h2>")
        elif button == QMessageBox.Cancel:
            self.ui.resultLabel.setText(
                "<h2>Question:<font color=red>  Cancel</font></h2>")
        else:
            return
```
除此之外，还需要一个程序入口.新建"main.py"
```python
# -*- coding: utf-8 -*-
import sys
from PyQt5.QtWidgets import QApplication
import Handler_dlg_main

if __name__ == "__main__":
    app = QApplication(sys.argv)
    with open('black.qss') as file:
        str = file.readlines()
        str =''.join(str).strip('\n')
    app.setStyleSheet(str)
    login = Handler_dlg_main.Handler_DlgMain()
    login.show()
    sys.exit(app.exec_())
```
上述代码以新建的dlg_main.ui为启动窗口, 并且还添加全局qss样式文件.

## 源代码
[源代码](pyqt.zip)  

