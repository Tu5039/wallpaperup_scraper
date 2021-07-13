# coding=utf-8
import requests
import re
import os
import time
from bs4 import BeautifulSoup
import traceback
import sys

page_num = 1  # 这里填写页数
sleep_time = 5  # 防止被断开连接
with open('log.txt', 'w'):  # 创建空文件来记录日志（多次运行的时候覆盖原有纪录）
    pass
while page_num <= 500:  # 设置最后一页
    try:
        # 输出到命令台以及日志文件
        print(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) +
              ' page_num = '+str(page_num))
        with open('log.txt', 'a') as log:
            log.write(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) +
                      ' page_num = '+str(page_num)+'\n')

        # 设置爬取的地址
        main_url = 'https://www.wallpaperup.com/search/results/'

        # 设置筛选条件
        option = {
            'cats_ids': '',  # 类别，自行修改为需要的类别的编号
            # 'cats_ids': '1',  # example

            'license': '',  # 版权，自行修改为需要的版权的编号
            # 'license': '1',  # example

            'ratio': '',  # 长宽比，
            # 'ratio': str(round(16/9, 2)),  # example 这里是16:9

            # 'resolution_mode': '',  # 分辨率筛选模式
            'resolution_mode': ':',  # 这里是at least
            # 'resolution_mode': ':=:',  # 这里是exactly

            # 'resolution': '',  # 分辨率，
            'resolution': '2560x1440',  # example 这里是2560*1440

            'color': '',
            # 'color': '#80c0e0',  # 颜色，自行修改颜色的编码
            # 'oder': '',  # 自行根据需要修改
            'order': 'date_added',  # 排序
        }

        # 生成url
        url = '' + main_url
        for key in option.keys():
            if option[key] == '' or key == 'resolution_mode':
                pass
            elif option[key] == 'resolution':
                url += (key + option['resolution_mode'] + option[key])
            else:
                url += (key + ':' + option[key])
                url += "+"
        url = url[:-1]+"/"+str(page_num)
        print(url)
        with open("log.txt", "a") as log:
            log.write(url)

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        }
        r_url = requests.get(url, headers=headers)
        print('解析中.....')
        with open('log.txt', 'a') as log:
            log.write(time.strftime("%Y-%m-%d %H:%M:%S",
                                    time.localtime())+'解析中.....\n')
            log.close()
        soup_a = BeautifulSoup(r_url.text, 'lxml')
        r_url.close()  # 关闭连接以防止被拒绝

        # 筛选链接
        wallpaper_pages = []
        for links in soup_a.find_all(attrs={'title': "View wallpaper"}):
            soup2 = BeautifulSoup(str(links), 'lxml')
            wallpaper_pages.append(
                'https://www.wallpaperup.com'+str(soup2.a.attrs['href']))

        wallpaper_imgaes_link = []
        for page in wallpaper_pages:
            r_page = requests.get(page, headers=headers)
            soup_page = BeautifulSoup(r_page.text, 'lxml')
            div_img = str(
                (soup_page.find_all(attrs={'class': 'thumb-wrp'}))[0])
            soup_div_img = BeautifulSoup(div_img, 'lxml')
            wallpaper_imgaes_link.append(
                str(soup_div_img.div.img.attrs['data-original']))

        # 新建文件夹，用以存放下载的图片
        wallpapers_folder = './Wallpaperup/'
        if os.path.exists(wallpapers_folder) == False:
            os.makedirs(wallpapers_folder)  # 这里使用makedirs来创建多级目录，mkdir只能建立一级

        p_split_name = re.compile(r'/')
        imageNumMax = len(wallpaper_imgaes_link)
        imageNumMin = 1
        print(str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))+' 解析完成.....')
        with open('log.txt', 'a') as log:
            log.write(str(time.strftime("%Y-%m-%d %H:%M:%S",
                                        time.localtime())) + ' 解析完成.....\n')
            log.close()
        for image_link in wallpaper_imgaes_link:
            print(str(imageNumMin)+'/'+str(imageNumMax)+' ' +
                  str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))+' '+image_link)
            with open('log.txt', 'a+') as log:
                log.write(str(imageNumMin)+'/'+str(imageNumMax) +
                          str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))+' \n')
            r_image_link = requests.get(image_link, headers=headers)
            filename = str(re.compile(r"\d{4}\/\d{2}\/\d{2}\/\d+").findall(
                image_link)[0]).replace("/", "", 2).replace("/", "_")+".jpg"
            print("filename=", filename)
            with open(wallpapers_folder+filename, 'wb+') as f:
                f.write(r_image_link.content)
            imageNumMin = imageNumMin+1
        page_num += 1
        sleep_time = 5  # 连接成功之后重置失败重试等待时间
    except Exception as e:
        traceback.print_exc()
        # 这里其实不一定是连接的问题，只是我在用的过程中基本上是，所以就给出这个提示，并且挂起几秒钟然后重新连接
        print('连接被关闭，正在重试...')
        with open('log.txt', 'a') as log:
            log.write('连接被关闭，正在重试...\n')
        time.sleep(sleep_time)
        sleep_time += 5
