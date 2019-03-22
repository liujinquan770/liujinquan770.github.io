import argparse
import json
import os.path
import random
import shutil
import sys
import time
import datetime

import tushare as ts
import xlrd
import xlsxwriter
from gooey import Gooey, GooeyParser
from win32com.client import Dispatch, constants

# 随机颜色值


def r(): return random.randint(0, 255)


class BasicData(object):
    '''
    '''

    def __init__(self):
        super(BasicData, self).__init__()
        self.code = 0.0
        self.name = 0.0


class MyData(object):
    '''
    源数据的数据结构
    '''

    def __init__(self):
        super(MyData, self).__init__()
        self.open = 0.0
        self.high = 0.0
        self.close = 0.0
        self.low = 0.0
        self.volume = 0.0
        self.price_change = 0.0
        self.p_change = 0.0
        self.ma5 = 0.0
        self.ma10 = 0.0
        self.ma20 = 0.0
        self.v_ma5 = 0.0
        self.v_ma10 = 0.0
        self.v_ma20 = 0.0
        self.turnover = 0.0


SOURCE_COL_DATE = 0
SOURCE_COL_OPEN = 1
SOURCE_COL_HIGH = 2
SOURCE_COL_CLOSE = 3
SOURCE_COL_LOW = 4
SOURCE_COL_VOLUME = 5
SOURCE_COL_P_CHANGE = 7

source_cols_en = [
    'date',
    'open',
    'high',
    'close',
    'low',
    'volume',
    'price_change',
    'p_change',
    'ma5',
    'ma10',
    'ma20',
    'v_ma5',
    'v_ma10',
    'v_ma20',
    'turnover',
]
source_cols_cn = [
    '日期',
    '开盘价',
    '最高价',
    '收盘价',
    '最低价',
    '成交量',
    '价格变动',
    '涨跌幅',
    '5日均价',
    '10日均价',
    '20日均价',
    '5日均量',
    '10日均量',
    '20日均量',
    '换手率',
]
dest_cols_cn = [
    '时间',
    '开盘',
    '最高',
    '最低',
    '收盘',
    '涨幅',
    '振幅',
    '总手',
    '金额',
    '换手',
    '成交次数',
    'KP移动平均值',
    'KP标准差',
    'Z',
    'CV',
    'KP-1SD',
    'KP+1SD',
    'KP-2SD',
    'KP+2SD',
    'KP-3SD',
    'KP+3SD',
    '开盘中位数',
    'KP-1SD',
    'KP+1中位',
    'KP-2中位',
    'KP+2中位',
    'KP-3中位',
    'KP+3中位',
    '开盘众位数',
    'KP-1SD',
    'KP+1中位',
    'KP-2中位',
    'KP+2中位',
    'KP-3中位',
    'KP+3中位',
    'SP移动平均值',
    'SP标准差',
    'Z',
    'CV',
    'SP-1SD',
    'SP+1SD',
    'SP-2SD',
    'SP+2SD',
    'SP-3SD',
    'SP+3SD',
    'S盘中位数',
    'SP-1SD',
    'SP+1SD',
    'SP-2SD',
    'SP+2SD',
    'SP-3SD',
    'SP+3SD',
    '开盘众位数',
    'SP-1SD',
    'SP+1SD',
    'SP-2SD',
    'SP+2SD',
    'SP-3SD',
    'SP+3SD',
    '量移平均值',
    '量标准差',
    'Z',
    'CV',
    '量-1SD',
    '量+1SD',
    '量-2SD',
    '量+2SD',
    '量-3SD',
    '量+3SD',
    '量盘中位数',
    '量-1SD',
    '量+1SD',
    '量-2SD',
    '量+2SD',
    '量-3SD',
    '量+3SD',
    '量众位数',
    '量-1SD',
    '量+1SD',
    '量-2SD',
    '量+2SD',
    '量-3SD',
    '量+3SD',
    '开盘-(KP-3SD)',
    '(KP+3SD)-开盘',
    '0线',
    '收盘-(SP-3SD)',
    '(SP+3SD)-收盘',
]


class ParseStockData(object):
    '''
    下载并分析股票历史数据
    '''
    dic_data = {}
    dic_code = {}
    nrows = 0
    ncols = 0
    workbook = None
    filename = 'new001.xlsx'
    stock_codes = []
    list_colors = [
        '#FF0000',
        '#336666',
        '#3399CC',
        '#6666FF',
        '#FF33CC',
        '#009966',
        '#FFCC33',
        '#FFFF00',
        '#000000',
    ]
    xlsApp = None

    def __init__(self):
        super(ParseStockData, self).__init__()
        # self.stock_codes = [
        #     x for x in ts.get_stock_basics().ix[:, :].index.values]
        try:
            now = datetime.datetime.now()
            valid_zip = 'valid_{0}'.format(now.strftime('%Y%m%d_%H%M%S'))
            invalid_zip = 'invalid_{0}'.format(now.strftime('%Y%m%d_%H%M%S'))
            if os.path.exists('valid'):
                shutil.make_archive(valid_zip, 'zip', 'valid')
                shutil.rmtree('valid')
            if os.path.exists('invalid'):
                shutil.make_archive(invalid_zip, 'zip', 'invalid')
                shutil.rmtree('invalid')
            self.xlsApp = Dispatch("Excel.Application")
        except:
            pass
        self.ReadBasic()
        self.stock_codes = list(self.dic_code.keys())

    def __del__(self):
        self.xlsApp.Quit()

    def ReadBasic(self, filename='basics.xlsx'):
        if not os.path.isfile(filename):
            print('basics.xlsx not exist')
            sys.exit(0)
        data = xlrd.open_workbook(filename)
        data.sheet_names()
        table = data.sheet_by_index(0)
        nrows = table.nrows
        for i in range(2, nrows):
            code = table.cell_value(i, 0)
            name = table.cell_value(i, 1)
            basic_data = BasicData()
            basic_data.code = code
            basic_data.name = name
            self.dic_code[code] = basic_data
        data.release_resources()
        del data

    def ReadTodic(self, filename):
        if not os.path.isfile(filename):
            print('file not exist')
            sys.exit()
        data = xlrd.open_workbook(filename, on_demand=True)
        data.sheet_names()
        table = data.sheet_by_index(0)
        nrows = table.nrows
        ncols = table.ncols
        for i in reversed(range(1, nrows)):
            key = table.cell_value(i, SOURCE_COL_DATE)
            cell_open = table.cell_value(i, SOURCE_COL_OPEN)
            cell_high = table.cell_value(i, SOURCE_COL_HIGH)
            cell_close = table.cell_value(i, SOURCE_COL_CLOSE)
            cell_low = table.cell_value(i, SOURCE_COL_LOW)
            cell_low = table.cell_value(i, SOURCE_COL_LOW)
            cell_volume = table.cell_value(i, SOURCE_COL_VOLUME)
            cell_p_change = table.cell_value(i, SOURCE_COL_P_CHANGE)
            mydata = MyData()
            mydata.open = cell_open
            mydata.high = cell_high
            mydata.close = cell_close
            mydata.low = cell_low
            mydata.volume = int(cell_volume*100)
            mydata.p_change = cell_p_change
            self.dic_data[key] = mydata
        # print(json.dumps(dic_data, default=lambda obj: obj.__dict__))
        data.release_resources()
        del data

    def DrawChart(self, worksheet, row_cnt,  n=20, title='开盘', cols=['B', 'L', 'V'], position='D619'):
        row_cnt = len(self.dic_data)+1
        sheet_name = "{0}日".format(n)
        # worksheet = workbook.get_worksheet_by_name(sheet_name)
        chart1 = self.workbook.add_chart({'type': 'line'})
        i = 0
        for col in cols:
            chart1.add_series({
                # 这里的sheet1是默认的值，因为我们在新建sheet时没有指定sheet名
                # 如果我们新建sheet时设置了sheet名，这里就要设置成相应的值
                'name': '={0}!${1}$1'.format(sheet_name, col),
                'categories': '={0}!$A${1}:$A${2}'.format(sheet_name, row_cnt-n, row_cnt),
                'values': '={0}!${3}${1}:${3}${2}'.format(sheet_name, row_cnt-n, row_cnt, col),
                'line': {'color': self.list_colors[i]},
                # 'line': {'color': '#{0:02X}{1:02X}{2:02X}'.format(r(), r(), r())},
            })
            i = i+1

        chart1.set_title({'name': title})
        chart1.set_x_axis({'name': '日期'})
        chart1.set_y_axis({'name': '价格'})
        # Set an Excel chart style. Colors with white outline and shadow.
        chart1.set_style(1)
        chart1.set_size({'width': 720, 'height': 576})
        # Insert the chart into the worksheet (with an offset).
        worksheet.insert_chart(
            position, chart1, {'x_offset': 0, 'y_offset': 0})

    def OpenXlsx(self, filename=None):
        if filename is not None:
            self.filename = filename
        else:
            self.filename = "new001.xlsx"
        self.workbook = xlsxwriter.Workbook(self.filename)

    def CloseXlsx(self):
        self.workbook.close()

    def DownloadSourceData(self, code='000001', start=None, end=None):
        data = ts.get_hist_data(code, start=start, end=end)  # 一次性获取全部日k线数据
        data.to_excel(self.filename)

    def DownAndParseStockCode(self, code='000001', start=None, end=None, days='20,30,50,60,90'):
        # print(json.dumps(self.dic_code, default=lambda obj: obj.__dict__))
        if code in self.dic_code.keys():
            self.filename = "{0}({1}).xlsx".format(
                self.dic_code[code].name, code)
        else:
            self.filename = "{0}.xlsx".format(code)
        print(self.filename)
        print('start download stock his data')
        self.DownloadSourceData(code, start=start, end=end)
        print('finish download stock his data')
        #
        self.ReadTodic(self.filename)
        print('finish read data from xlsx')
        self.OpenXlsx(self.filename)

        days_str = days.split(',')
        for d in days_str:
            day = int(d)
            a, b, c, d, e, f = self.NewSheet(day)
            print(a, b, c, d, e, f)
            print('create {0} days sheet'.format(day))
        self.CloseXlsx()
        print('all done.')

    def DownAndClassifyStockCode(self, code='000001', start=None, end=None, days='50', classify=50, factor=0.95):
        if code in self.dic_code.keys():
            self.filename = "{0}({1}).xlsx".format(
                self.dic_code[code].name.replace('*', ''), code)
        else:
            self.filename = "{0}.xlsx".format(code)
        print(self.filename)
        print('start download stock his data')
        self.DownloadSourceData(code, start=start, end=end)
        print('finish download stock his data')
        #
        time.sleep(0.1)
        self.ReadTodic(self.filename)
        time.sleep(0.1)
        print('finish read data from xlsx')
        self.OpenXlsx(self.filename)

        dic_classify = {}
        days_str = days.split(',')
        for d in days_str:
            day = int(d)
            dic_classify[day] = self.NewSheet(day)
            print('create {0} days sheet'.format(day))
        self.CloseXlsx()
        try:
            time.sleep(0.2)
            self.OpenAndSave()
            time.sleep(0.5)
        except Exception as e:
            print("Exception error: {0}".format(e))

        print('factor2={0}'.format(factor))
        self.Classify(positions=dic_classify[classify], n=classify, f=factor)
        print('all done.')

    def Classify(self, positions, n=50,  f=0.95):
        if not os.path.isfile(self.filename):
            print('{0} not exist'.format(self.filename))
            sys.exit(0)

        correl_cell, pearson_cell, kpf1_col, kpf2_col, sff1_col, sff2_col = positions
        sheet_name = "{0}日".format(n)
        data = xlrd.open_workbook(self.filename, on_demand=True)
        data.sheet_names()
        table = data.sheet_by_name(sheet_name)

        correl_value = table.cell_value(correl_cell[0], correl_cell[1])
        pearson_value = table.cell_value(pearson_cell[0], pearson_cell[1])
        col_kpf1 = table.col_values(kpf1_col)[-n-1:-1]
        col_kpf1 = [x for x in col_kpf1 if isinstance(x, float)]
        col_kpf1_lt_0 = [x for x in col_kpf1 if float(x) < 0.0]

        col_kpf2 = table.col_values(kpf2_col)[-n-1:-1]
        col_kpf2 = [x for x in col_kpf2 if isinstance(x, float)]
        col_kpf2_lt_0 = [x for x in col_kpf2 if float(x) < 0.0]

        col_kff1 = table.col_values(sff1_col)[-n-1:-1]
        col_kff1 = [x for x in col_kff1 if isinstance(x, float)]
        col_kff1_lt_0 = [x for x in col_kff1 if float(x) < 0.0]

        col_kff2 = table.col_values(sff2_col)[-n-1:-1]
        col_kff2 = [x for x in col_kff2 if isinstance(x, float)]
        col_kff2_lt_0 = [x for x in col_kff2 if float(x) < 0.0]
        print(correl_value, pearson_value, col_kpf1_lt_0,
              col_kpf2_lt_0, col_kff1_lt_0, col_kff2_lt_0)

        data.release_resources()
        del data
        # (correl_value > f*100) and (pearson_value > f*100) and
        # 取不到值
        is_valid = (correl_value > f*100) and (pearson_value > f*100) and (len(col_kpf1_lt_0) == 0) and (
            len(col_kpf2_lt_0) == 0) and (len(col_kff1_lt_0) == 0) and (len(col_kff2_lt_0) == 0)
        if is_valid:
            self.mkdir('valid')
            shutil.move(self.filename, 'valid')
        else:
            self.mkdir('invalid')
            shutil.move(self.filename, 'invalid')

    def mkdir(self, path):
        folder = os.path.exists(path)
        if not folder:
            os.makedirs(path)

    def OpenAndSave(self):
        dirs = os.path.split(os.path.realpath(__file__))[0]
        # print(dirs)
        abs_path = os.path.join(dirs, self.filename)
        # 通过赋值Visible为True或者False可以控制是否调出excle
        self.xlsApp.Visible = 0
        xlsBook = self.xlsApp.Workbooks.Open(abs_path)
        # xlsBook.SaveAs(abs_path)
        xlsBook.Save()
        xlsBook.Close()

    def NewSheet(self, n=50):
        correl_cell = (0, 0)
        pearson_cell = (0, 0)
        kpf1_col = 0
        kpf2_col = 0
        sff1_col = 0
        sff2_col = 0

        worksheet = self.workbook.add_worksheet("{0}日".format(n))
        worksheet.set_column(0, len(dest_cols_cn))
        align_right = self.workbook.add_format({'align': 'right'})

        for i in range(len(dest_cols_cn)):
            worksheet.write(0, i, dest_cols_cn[i])
        row = 1
        for k, v in self.dic_data.items():
            col = 0
            worksheet.write(row, col, k)
            col = col + 1
            worksheet.write(row, col, v.open)
            col = col + 1
            worksheet.write(row, col, v.high)
            col = col + 1
            worksheet.write(row, col, v.low)
            col = col + 1
            worksheet.write(row, col, v.close)
            col = col + 1
            worksheet.write(row, col, str(v.p_change)+'%', align_right)  # 涨幅
            col = col + 1
            worksheet.write(row, col, None)  # 振幅
            col = col + 1
            worksheet.write(row, col, v.volume)  # 总手
            col = col + 1
            worksheet.write(row, col, None)  # 金额
            col = col + 1
            worksheet.write(row, col, None)  # 换手
            col = col + 1
            worksheet.write(row, col, None)  # 成交次数
            # worksheet.write(row, 11, None)  # KP移动值
            # worksheet.write(row, 12, None)  # KP标准差
            if row > n:
                # KP移动值
                col = col + 1
                formula = '=AVERAGE(B{0}:B{1})'.format(row-n+1, row+1)
                worksheet.write_formula(row, col, formula)
                # KP标准差
                col = col + 1
                formula = '=STDEVP(B{0}:B{1})'.format(row-n+1, row+1)
                worksheet.write_formula(row, col, formula)
                # Z
                col = col + 1
                formula = '=(B{0}-L{0})/M{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # CV
                col = col + 1
                formula = '=M{0}/L{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # KP-1SD
                col = col + 1
                formula = '=L{0}-M{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # KP+1SD
                col = col + 1
                formula = '=L{0}+M{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # KP-2SD
                col = col + 1
                formula = '=L{0}-2*M{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # KP+2SD
                col = col + 1
                formula = '=L{0}+2*M{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # KP-3SD
                col = col + 1
                formula = '=L{0}-3*M{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # KP+3SD
                col = col + 1
                formula = '=L{0}+3*M{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # 开盘中位数
                col = col + 1
                formula = '=MEDIAN(B{0}:B{1})'.format(row+1-n, row+1)
                worksheet.write_formula(row, col, formula)
                # KP-1SD
                col = col + 1
                formula = '=V{0}-M{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # KP+1中位 =V165+M165
                col = col + 1
                formula = '=V{0}+M{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # KP-2中位
                col = col + 1
                formula = '=V{0}-2*M{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # KP+2中位
                col = col + 1
                formula = '=V{0}+2*M{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # KP-3中位
                col = col + 1
                formula = '=V{0}-3*M{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # KP+3中位
                col = col + 1
                formula = '=V{0}+3*M{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # 开盘众位数 =MODE(B143:B163)
                col = col + 1
                formula = '=MODE(B{0}:B{1})'.format(row+1-n, row+1)
                worksheet.write_formula(row, col, formula)
                # KP-1SD =AC163-M163
                col = col + 1
                formula = '=AC{0}-M{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # KP+1中位
                col = col + 1
                formula = '=AC{0}+M{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # KP-2中位
                col = col + 1
                formula = '=AC{0}-2*M{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # KP+2中位
                col = col + 1
                formula = '=AC{0}+2*M{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # KP-3中位
                col = col + 1
                formula = '=AC{0}-3*M{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # KP+3中位
                col = col + 1
                formula = '=AC{0}+3*M{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)

                # SP移动平均值 =AVERAGE(E143:E163)
                col = col + 1
                formula = '=AVERAGE(E{0}:E{1})'.format(row+1-n, row+1)
                worksheet.write_formula(row, col, formula)
                # SP标准差 =STDEVP(E143:E163)
                col = col + 1
                formula = '=STDEVP(E{0}:E{1})'.format(row+1-n, row+1)
                worksheet.write_formula(row, col, formula)
                # Z  =(E163-AJ163)/AK163
                col = col + 1
                formula = '=(E{0}-AJ{0})/AK{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # CV =AK163/AJ163
                col = col + 1
                formula = '=AK{0}/AJ{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # SP-1SD =AJ164-AK164
                col = col + 1
                formula = '=AJ{0}-AK{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # SP+1SD
                col = col + 1
                formula = '=AJ{0}+AK{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # SP-2SD
                col = col + 1
                formula = '=AJ{0}-2*AK{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # SP+2SD
                col = col + 1
                formula = '=AJ{0}+2*AK{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # SP-3SD
                col = col + 1
                formula = '=AJ{0}-3*AK{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # SP+3SD
                col = col + 1
                formula = '=AJ{0}+3*AK{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)

                # S盘中位数 =MEDIAN(E143:E163)
                col = col + 1
                formula = '=MEDIAN(E{0}:E{1})'.format(row+1-n, row+1)
                worksheet.write_formula(row, col, formula)
                # SP-1SD =AT163-AK163
                col = col + 1
                formula = '=AT{0}-AK{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # SP+1SD
                col = col + 1
                formula = '=AT{0}+AK{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # SP-2SD
                col = col + 1
                formula = '=AT{0}-2*AK{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # SP+2SD
                col = col + 1
                formula = '=AT{0}+2*AK{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # SP-3SD
                col = col + 1
                formula = '=AT{0}-3*AK{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # SP+3SD
                col = col + 1
                formula = '=AT{0}+3*AK{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)

                # 开盘众位数 =MODE(E143:E163)
                col = col + 1
                formula = '=MODE(E{0}:E{1})'.format(row+1-n, row+1)
                worksheet.write_formula(row, col, formula)
                # SP-1SD =AT163-AK163
                col = col + 1
                # formula = '=AT{0}-AK{0}'.format(row+1)
                worksheet.write(row, col, None)
                # SP+1SD
                col = col + 1
                # formula = '=AT{0}+AK{0}'.format(row+1)
                worksheet.write(row, col, None)
                # SP-2SD
                col = col + 1
                # formula = '=AT{0}-2*AK{0}'.format(row+1)
                worksheet.write(row, col, None)
                # SP+2SD
                col = col + 1
                # formula = '=AT{0}+2*AK{0}'.format(row+1)
                worksheet.write(row, col, None)
                # SP-3SD
                col = col + 1
                # formula = '=AT{0}-3*AK{0}'.format(row+1)
                worksheet.write(row, col, None)
                # SP+3SD
                col = col + 1
                # formula = '=AT{0}+3*AK{0}'.format(row+1)
                worksheet.write(row, col, None)

                # 量移动平均值 =AVERAGE(H143:H163)
                col = col + 1
                formula = '=AVERAGE(H{0}:H{1})'.format(row+1-n, row+1)
                worksheet.write_formula(row, col, formula)
                # 量标准差 =STDEVP(H143:H163)
                col = col + 1
                formula = '=STDEVP(H{0}:H{1})'.format(row+1-n, row+1)
                worksheet.write_formula(row, col, formula)
                # Z  =(H163-BH163)/BI163
                col = col + 1
                formula = '=(H{0}-BH{0})/BI{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # CV =BI163/BH163
                col = col + 1
                formula = '=BI{0}/BH{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # 量-1SD =BH163-BI163
                col = col + 1
                formula = '=BH{0}-BI{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # 量+1SD
                col = col + 1
                formula = '=BH{0}+BI{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # 量-2SD
                col = col + 1
                formula = '=BH{0}-2*BI{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # 量+2SD
                col = col + 1
                formula = '=BH{0}+2*BI{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # 量-3SD
                col = col + 1
                formula = '=BH{0}-3*BI{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # 量+3SD
                col = col + 1
                formula = '=BH{0}+3*BI{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)

                # 量盘中位数 =MEDIAN(H143:H163)
                col = col + 1
                formula = '=MEDIAN(H{0}:H{1})'.format(row+1-n, row+1)
                worksheet.write_formula(row, col, formula)
                # 量-1SD =BR163-BI163
                col = col + 1
                formula = '=BR{0}-BI{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # 量+1SD
                col = col + 1
                formula = '=BR{0}+BI{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # 量-2SD
                col = col + 1
                formula = '=BR{0}-2*BI{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # 量+2SD
                col = col + 1
                formula = '=BR{0}+2*BI{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # 量-3SD
                col = col + 1
                formula = '=BR{0}-3*BI{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # 量+3SD
                col = col + 1
                formula = '=BR{0}+3*BI{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                # 开盘-(KP-3SD) =B52-T52
                col = col + 8
                formula = '=B{0}-T{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                kpf1_col = col
                # (KP+3SD)-开盘 =U52-B52
                col = col + 1
                formula = '=U{0}-B{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                kpf2_col = col
                # 0线 =0
                col = col + 1
                # formula = '=U{0}-B{0}'.format(row+1)
                worksheet.write(row, col, 0)
                # 收盘-(SP-3SD) =E52-AR52
                col = col + 1
                formula = '=E{0}-AR{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                sff1_col = col
                # (SP+3SD)-收盘 =AS52-E52
                col = col + 1
                formula = '=AS{0}-E{0}'.format(row+1)
                worksheet.write_formula(row, col, formula)
                sff2_col = col
            row = row + 1
        # 开盘收盘相关系数
        # =CORREL(B133:B182,E133:E182)
        row1 = row
        formula = '=INT(CORREL(B{0}:B{1},E{0}:E{1})*100)'.format(row-n+1, row)
        worksheet.write_formula(row1, 0, formula)
        correl_cell = (row1, 0)
        # print('correl_cell col is ' + str(row1))
        # 开盘收盘皮尔逊相关系数
        # =PEARSON(B133:B182,E133:E182)
        row1 = row
        formula1 = '=INT(PEARSON(B{0}:B{1},E{0}:E{1})*100)'.format(row-n+1, row)
        worksheet.write_formula(row1, 1, formula1)
        pearson_cell = (row1, 1)
        # 绘制图表
        row1 = row + 10
        position_chart = 'D{0}'.format(row1)
        self.DrawChart(worksheet=worksheet, row_cnt=row, n=n, title="开盘线分析",
                       cols=['CF', 'CG', 'CH'], position=position_chart)
        row1 += 30
        position_chart = 'D{0}'.format(row1)
        self.DrawChart(worksheet=worksheet, row_cnt=row, n=n, title="收盘线分析",
                       cols=['CI', 'CJ', 'CH'], position=position_chart)
        row1 += 30
        position_chart = 'D{0}'.format(row1)
        self.DrawChart(worksheet=worksheet, row_cnt=row, n=n, title="开盘1",
                       cols=['B', 'L', 'V'], position=position_chart)
        row1 += 30
        position_chart = 'D{0}'.format(row1)
        self.DrawChart(worksheet=worksheet, row_cnt=row, n=n, title="开盘2",
                       cols=['B', 'P', 'Q', 'R', 'S', 'T', 'U'], position=position_chart)
        row1 += 30
        position_chart = 'D{0}'.format(row1)
        self.DrawChart(worksheet=worksheet, row_cnt=row, n=n, title="开盘中位数",
                       cols=['V', 'W', 'X', 'Y', 'Z', 'AA', 'AB', ], position=position_chart)
        row1 += 30
        position_chart = 'D{0}'.format(row1)
        self.DrawChart(worksheet=worksheet, row_cnt=row, n=n, title="收盘1",
                       cols=['E', 'AJ', 'AT'], position=position_chart)
        row1 += 30
        position_chart = 'D{0}'.format(row1)
        self.DrawChart(worksheet=worksheet, row_cnt=row, n=n, title="收盘2",
                       cols=['E', 'AN', 'AO', 'AP', 'AQ', 'AR', 'AS'], position=position_chart)
        row1 += 30
        position_chart = 'D{0}'.format(row1)
        self.DrawChart(worksheet=worksheet, row_cnt=row, n=n, title="开盘-收盘",
                       cols=['B', 'E', ], position=position_chart)

        return (correl_cell, pearson_cell, kpf1_col, kpf2_col, sff1_col, sff2_col)


@Gooey()
def main1():
    import datetime
    now = datetime.datetime.now()
    diff = datetime.timedelta(days=-270)
    before = now+diff

    start = before.strftime('%Y-%m-%d')
    end = now.strftime('%Y-%m-%d')
    parser = GooeyParser(description='下载并分析股票历史数据')
    parser.add_argument('mode', choices=[
                        '单个股票', '所有股票'], help='单个股票，下载并生成指定股票的图表数据；所有股票，下载并分类', default='单个股票')
    parser.add_argument(
        '-f', '--factor', help='相关性系数, 超过该值则入选', default=0.98, type=float)
    parser.add_argument('-c', '--code', help='股票代码', default='000001')
    parser.add_argument(
        '-s', '--start', help='开始日期,格式YYYY-MM-DD', default=start)
    parser.add_argument('-e', '--end', help='结束日期,格式YYYY-MM-DD', default=end)
    parser.add_argument(
        '-d', '--days', help='时间跨度,逗号分隔,20=不离线,50=布朗运动...', default='20,30,50,60,90')
    args = parser.parse_args()

    mode = args.mode
    print(mode)

    if mode == '所有股票':
        factor = args.factor
        print(factor)
        main3(factor)
    else:
        stock_code = args.code
        start_date = args.start
        end_date = args.end
        days = args.days
        print('stock code is ' + stock_code)

        parse1 = ParseStockData()
        if stock_code not in parse1.stock_codes:
            print(stock_code + ' is invalid')
            return
        # 2
        parse1.DownAndParseStockCode(
            code=stock_code, start=start_date, end=end_date, days=days)


def main2():
    # os.system('taskkill /IM EXCEL.exe /F')
    now = datetime.datetime.now()
    diff = datetime.timedelta(days=-180)
    before = now+diff

    start = before.strftime('%Y-%m-%d')
    end = now.strftime('%Y-%m-%d')
    parse2 = ParseStockData()
    for stock_code in sorted(parse2.stock_codes):
        try:
            parse2.DownAndClassifyStockCode(
                code=stock_code, start=start, end=end)
        except Exception as e:
            print("Exception error: {0}".format(e))


from multiprocessing import Pool


def main3_child(codes, start, end, factor=0.95):
    parse2 = ParseStockData()
    for stock_code in codes:
        try:
            print('factor1={0}'.format(factor))
            parse2.DownAndClassifyStockCode(
                code=stock_code, start=start, end=end, factor=factor)
        except Exception as e:
            print("Exception error: {0}".format(e))


def main3(factor=0.8):
    now = datetime.datetime.now()
    diff = datetime.timedelta(days=-180)
    start = (now+diff).strftime('%Y-%m-%d')
    end = now.strftime('%Y-%m-%d')

    process_count = 2
    p = Pool(process_count)
    parse2 = ParseStockData()
    list_code = sorted(parse2.stock_codes)
    piece = int(len(list_code)/process_count)
    for i in range(process_count):
        index = i*piece
        if i == process_count-1:
            index2 = len(list_code)-1
        else:
            index2 = (i+1)*piece
        print(index, index2)
        sub_codes = list_code[index: index2]
        p.apply_async(main3_child, args=(sub_codes, start, end, factor))
    print('waiting for all subproces done..')
    p.close()
    p.join()
    print("all subprocess done")


if __name__ == "__main__":
    main1()
