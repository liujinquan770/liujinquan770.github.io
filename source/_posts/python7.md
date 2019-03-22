---
title: PYTHON笔记7 生成SQLSERVER数据表结构的WORD文档
date: 2018-08-04 10:16:02
modified: 
tags: [python]
categories: python
---

&nbsp;&nbsp;项目中数据库表结构经常变动，现在使用SQL脚本做版本管理。 为更直观的比较表结构变动，我们也做了一份WORD文档，以表格的方式记录这些表的表结构。  

![示例图片](python7/2018084.jpg)

<!--more-->


脚本中使用pymssql和win32.com库实现。其实这个脚本很早以前使用python2.7实现了，不过现在又有了这种需求，就从为知笔记里找出来修改成了python3版本。
```python
# coding:utf-8
# Author: liujinquan<120026492@qq.com>
# Purpose:
# Created: 2012-10-18
import sys
import os
import decimal
import pymssql
import configparser
from win32com.client import Dispatch, constants, DispatchEx
from win32com.client import DispatchEx
# WORD文档操作封装类


class WordWrap:
    """Wrapper aroud Word 8 documents to make them easy to build.
Has variables for the Applications, Document and Selection;
most methods add things at the end of the document"""

    def __init__(self, templatefile=None):
        self.wordApp = DispatchEx('Word.Application')
        # self.wordApp.Visible=0
        # self.wordApp.DisplayAlerts=0    #后台运行，不显示，不警告
        if templatefile == None:
            self.wordDoc = self.wordApp.Documents.Add()
        else:
            self.wordDoc = self.wordApp.Documents.Add(Template=templatefile)

        # set up the selection
        self.wordDoc.Range(0, 0).Select()
        self.wordSel = self.wordApp.Selection

    def show(self):
        # convenience when debugging
        self.wordApp.Visible = 1

    def getStyleList(self):
        # returns a dictionary of the styles in a document
        self.styles = []
        stylecount = self.wordDoc.Styles.Count
        for i in range(1, stylecount + 1):
            styleObject = self.wordDoc.Styles(i)
            self.styles.append(styleObject.NameLocal)

    def saveAs(self, filename):
        self.wordDoc.SaveAs(filename)

    def printout(self):
        self.wordDoc.PrintOut()

    def selectEnd(self):
        # ensures insertion point is at the end of the document
        self.wordSel.Collapse(0)
        # 0 is the constant wdCollapseEnd; don't weant to depend
        # on makepy support.

    def addText(self, text):
        self.wordSel.InsertAfter(text)
        self.selectEnd()

    def addStyledPara(self, text, stylename):
        if text[-1] != '\n':
            text = text + '\n'

        self.wordSel.InsertAfter(text)
        self.wordSel.Style = stylename
        self.selectEnd()

    def addTable(self, table, styleid=None):
        # Takes a 'list of lists' of data.
        # first we format the text. You might want to preformat
        # numbers with the right decimal places etc. first.
        textlines = []
        for row in table:
            textrow = map(str, row)  # convert to strings
            textline = '\t'.join(textrow)
            textlines.append(textline)
        text = '\n'.join(textlines)

        # add the text, which remains selected
        self.wordSel.InsertAfter(text)

        # convert to a table
        wordTable = self.wordSel.ConvertToTable(Separator='\t')
        # enable table border line
        wordTable.Borders.Enable = True
        # and format
        if styleid:
            wordTable.AutoFormat(Format=styleid)
        self.selectEnd()

    def addInlineExcelChart(self, filename, caption='', height=216, width=432):
        # adds a chart inline within the text, caption below.

        # add an InlineShape to the InlineShapes collection
        # - could appear anywhere
        shape = self.wordDoc.InlineShapes.AddOLEObject(
            ClassType='Excel.Chart',
            FileName=filename
        )
        # set height and width in points
        shape.Height = height
        shape.Width = width

        # put it where we want
        shape.Range.Cut()

        self.wordSel.InsertAfter('chart will replace this')
        self.wordSel.Range.Paste()  # goes in selection
        self.addStyledPara(caption, 'Normal')

    def quit(self, code=0):
        self.wordApp.Quit(code)


class ExportToWord:

    # ----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""
        self._word__ = None
        self._dbname__ = None

    # 获取Word实例
    def getWordWrap(self):
        if(self._word__ == None):
            self._word__ = WordWrap()
        return self._word__

    # 建立表格
    def exportToWord(self, columnTitle=None, dicData=None):
        '''
        columnTitle:列表,[字段序号,字段名,标识,主键,类型,占用字节,长度,小数位数,允许空,默认值,字段说明]
        dicData:字典，关键字√表名，内容√字段信息，每一行一个字段
        '''
        # WORD对象
        word = self.getWordWrap()
        # 排序
        listKeys = list(dicData.keys())
        listKeys.sort()
        # 生成表格
        for key in listKeys:
            # 标题
            word.addStyledPara(key, u'标题 3')
            table = []
            # 表头
            table.append(columnTitle)
            # 表内容
            table.extend(dicData.get(key, []))
            word.addTable(table)
            print(u'添加表%s' % key)
        # 保存文档
        print(u'正在保存文档...')
        path = '{0}\\{1}.docx'.format(os.path.split(
            os.path.realpath(__file__))[0], self._dbname__)
        print(path)
        word.saveAs(path)
        word.quit()


# 查询数据库用户表的表结构
    def getUserTableDefine(self, host='.', username='sa', password='swshare6_', dbname='LibDB', sql=None):
        '''
        host:数据库实例名
        username:登录用户
        password:登录密码
        dbname:数据库名称
        sql:查询表结构的SQL语句

        '''
        self._dbname__ = dbname
        # 查询
        con = pymssql.connect(host=host, user=username, charset='utf8',
                              password=password, database=dbname, as_dict=False)
        cur = con.cursor()
        cur.execute(sql)
        results = cur.fetchall()
        cur.close()
        con.close()
        # 根据结果建立字典
        dictResult = {}
        for row in results:
            #tableName = row[0]
            tableName = str(row[0]).replace(' ', '')
            if len(tableName) <= 0:
                continue
            if tableName not in dictResult:
                dictResult[tableName] = []
            row = list(row[1:])
            row[1] = str(row[1]).encode('latin1').decode('gbk')
            row[5] = str(row[5]).encode('latin1').decode('gbk')
            row[9] = row[9].decode('utf8')
            # row1 = [x.encode('latin1').decode('gbk') for x in row if isinstance(x, str)]
            dictResult[tableName].append(row)
        return dictResult

    # 获取脚本所在目录
    def GetScriptPath(self):

        # determine if application is a script file or frozen exe
        # 判断是EXE还是脚本文件
        application_path = None
        if getattr(sys, 'frozen', False):
            application_path = os.path.dirname(sys.executable)
        elif __file__:
            application_path = os.path.split(os.path.realpath(__file__))[0]
        return application_path


if __name__ == '__main__':

    # 查询表结构的SQL语句
    # sql = u'''
    # SELECT
    # 表名=d.name,
    # --字段序号=a.colorder,
    # 字段名=a.name,
    # 标识=case when COLUMNPROPERTY( a.id,a.name,'IsIdentity')=1 then '√'else '' end,
    # 主键=case when exists(SELECT 1 FROM sysobjects where xtype='PK' and name in (
    # SELECT name FROM sysindexes WHERE indid in(
    #     SELECT indid FROM sysindexkeys WHERE id = a.id AND colid=a.colid
    # ))) then '√' else '' end,
    # 类型=b.name,
    # 占用字节数=a.length,
    # 小数位数=isnull(COLUMNPROPERTY(a.id,a.name,'Scale'),0),
    # 允许空=case when a.isnullable=1 then '√'else '' end,
    # 默认值=isnull(e.text,''),
    # 字段说明=isnull(g.[value],'')
    # FROM syscolumns a
    # left join systypes b on a.xtype=b.xusertype
    # inner join sysobjects d on a.id=d.id and d.xtype='U' and d.name<>'dtproperties'
    # left join syscomments e on a.cdefault=e.id
    # left join sys.extended_properties g on a.id = g.major_id and a.colid = g.minor_id
    # order by 表名,字段序号 asc'''

    sql = u'''SELECT
    表名=CASE WHEN a.colorder = 1 THEN d.name ELSE d.name END,
    --表说明=CASE WHEN a.colorder = 1 THEN isnull(f.value, '') ELSE '' END ,
    --字段序号=a.colorder ,
    字段名=a.name ,
    --标识=CASE WHEN COLUMNPROPERTY(a.id, a.name, 'IsIdentity') = 1 THEN '√' ELSE '' END ,
    主键=CASE WHEN EXISTS (
                SELECT 1
                FROM dbo.sysindexes si
                        INNER JOIN dbo.sysindexkeys sik ON si.id = sik.id AND si.indid = sik.indid
                        INNER JOIN dbo.syscolumns sc ON sc.id = sik.id AND sc.colid = sik.colid
                        INNER JOIN dbo.sysobjects so ON so.name = so.name AND so.xtype = 'PK'
                WHERE sc.id = a.id AND sc.colid = a.colid) THEN '√'
                ELSE ''
        END ,
    外键=CASE WHEN tony.fkey is not null and tony.fkey=a.colid THEN '√' ELSE '' END ,
    --外键表=CASE WHEN tony.fkey is not null and tony.fkey=a.colid
    --        THEN object_name(tony.fkeyid) ELSE ''
    -- END ,
    --外键字段=CASE WHEN tony.fkey is not null and tony.fkey=a.colid
    --        THEN (SELECT name FROM syscolumns
    --               WHERE colid=tony.fkey AND id=tony.fkeyid) 
    --        ELSE ''
    --        END,
    类型=b.name ,
    长度=a.length ,
    --精度=COLUMNPROPERTY(a.id, a.name, 'PRECISION') ,
    --小数位数=ISNULL(COLUMNPROPERTY(a.id, a.name, 'Scale'), 0) ,
    允许空=CASE WHEN a.isnullable = 1 THEN '√' ELSE '' END ,
    默认值= ISNULL(e.text, ''),
    --创建时间=d.crdate,
    --更改时间=CASE WHEN a.colorder = 1 THEN d.refdate ELSE NULL END
    索引=ISNULL(IDX.IndexName,N''),
    索引顺序=ISNULL(IDX.Sort,N''),
    字段说明=ISNULL(g.[value], '')
    FROM dbo.syscolumns a
    LEFT JOIN dbo.systypes b ON a.xtype = b.xusertype
    INNER JOIN dbo.sysobjects d ON a.id = d.id AND d.xtype = 'U' AND d.status >= 0
    LEFT JOIN dbo.syscomments e ON a.cdefault = e.id
    LEFT JOIN sys.extended_properties g ON a.id = g.major_id AND a.colid = g.minor_id
    LEFT JOIN sys.extended_properties f ON d.id = f.major_id AND f.minor_id = 0 
    LEFT JOIN sysobjects htl ON htl.parent_obj=d.id AND htl.xtype='F'
    LEFT JOIN sysforeignkeys tony on htl.id=tony.constid
    LEFT JOIN                      -- 索引及主键信息
    (
        SELECT
                IDXC.[object_id],
                IDXC.column_id,
                Sort=CASE INDEXKEY_PROPERTY(IDXC.[object_id],IDXC.index_id,IDXC.index_column_id,'IsDescending')
                WHEN 1 THEN 'DESC' WHEN 0 THEN 'ASC' ELSE '' END,
                PrimaryKey=CASE WHEN IDX.is_primary_key=1 THEN N'√'ELSE N'' END,
                IndexName=IDX.Name
        FROM sys.indexes IDX
        INNER JOIN sys.index_columns IDXC
                ON IDX.[object_id]=IDXC.[object_id]
                AND IDX.index_id=IDXC.index_id
        LEFT JOIN sys.key_constraints KC
                ON IDX.[object_id]=KC.[parent_object_id]
                AND IDX.index_id=KC.unique_index_id
        INNER JOIN -- 对于一个列包含多个索引的情况,只显示第1个索引信息
        (
                SELECT [object_id], Column_id, index_id=MIN(index_id)
                FROM sys.index_columns
                GROUP BY [object_id], Column_id
        ) IDXCUQ
                ON IDXC.[object_id]=IDXCUQ.[object_id]
                AND IDXC.Column_id=IDXCUQ.Column_id
                AND IDXC.index_id=IDXCUQ.index_id
    ) IDX
        ON a.id = IDX.[object_id]
        AND A.colid = IDX.column_id
    --WHERE d.name='tb' --这里输入包含表名称的条件
    ORDER BY d.id, a.colorder'''
    # 表格表头
    columnTitle = [u'字段名', u'主键', u'外键', u'类型', u'长度',
                   u'允许空', u'默认值', u'索引', u'索引顺序', u'字段说明']

    # 主流程
    exportWord = ExportToWord()
    # 读配置文件
    print(u"正在读取配置文件...")
    config = configparser.ConfigParser()
    iniPath = r"%s\config.ini" % exportWord.GetScriptPath()
    config.read(iniPath)
    host = config.get("DB", "host")
    username = config.get("DB", "username")
    password = config.get("DB", "password")
    database = config.get("DB", "database")
    print(u'正在查询数据库...')
    dictResult = exportWord.getUserTableDefine(
        host, username, password, database, sql)
    exportWord.exportToWord(columnTitle, dictResult)
```


