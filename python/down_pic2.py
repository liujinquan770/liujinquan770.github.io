# 下载网络图片设置壁纸
# 2018/5/21 clz
# win10 ,python3.0

import datetime
import os
import re

import requests
import win32con

# import PIL.Image
import win32api
import win32gui
from bs4 import BeautifulSoup

os.makedirs('Bing', exist_ok=True)
dt = datetime.datetime.now()
dtAsFileNmae = str(dt.year) + '0' + str(dt.month) + str(dt.day)
img_path = os.path.abspath(os.path.join('Bing', dtAsFileNmae+'.jpg'))

print(img_path)


def set_wallpaper_from_bmp(bmp_path):
    # 打开指定注册表路径
    reg_key = win32api.RegOpenKeyEx(
        win32con.HKEY_CURRENT_USER, "Control Panel\\Desktop", 0, win32con.KEY_SET_VALUE)
    # 最后的参数:2拉伸,0居中,6适应,10填充,0平铺
    win32api.RegSetValueEx(reg_key, "WallpaperStyle", 0, win32con.REG_SZ, "2")
    win32api.RegSetValueEx(reg_key, "TileWallpaper", 0, win32con.REG_SZ, "0")
    # 刷新桌面
    win32gui.SystemParametersInfo(
        win32con.SPI_SETDESKWALLPAPER, bmp_path, win32con.SPIF_SENDWININICHANGE)


def set_wallpaper(bmp_path):
    img_dir = os.path.dirname(bmp_path)
    bmpImg = PIL.Image.open(bmp_path)
    new_bmp_path = os.path.join(img_dir, 'wallpaper.bmp')
    bmpImg.save(new_bmp_path, "BMP")
    set_wallpaper_from_bmp(new_bmp_path)


def getTopPictureFromBingWallpaper():
    # 从Bing当日美图下载第一幅图片
    url = 'http://bing-wallpaper.com/cn'
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    imageLst = soup.select('.cursor_zoom img')
    image_url = imageLst[0].get('src')
    res = requests.get(image_url)
    with open(img_path, 'wb') as file:
        file.write(res.content)
    # from PIL import Image
    # im = Image.open(img_path)
    # (x, y) = im.size
    # (x, y) = (int(x), int(y))
    # out = im.resize((int(x/2), int(y/2)), Image.ANTIALIAS)
    # out.save(img_path)


if __name__ == '__main__':
    getTopPictureFromBingWallpaper()
    # set_wallpaper(img_path)
# a = input('please input any key to continue!')
