# -*- coding: utf-8 -*-
import os
import os.path
import socket
import urllib.parse
import urllib.request
import gzip
import traceback

from bs4 import BeautifulSoup
from urllib.error import HTTPError


class MeituluSpider(object):
    item_url = "https://www.meitulu.com/item/%d.html"
    item_url_next = "https://www.meitulu.com/item/%d_%d.html"
    page_max = 99999

    # 要下载的图片主题
    items = [133, 9830]
    items = range(134, 199)
    items = [133,9830]
    items = range(0,99)
    items = range(0, 99999)
    items = [12471,12460,9836,8447,3055,2770,2593,2592,2314,1831,1828,1784,1767,1745,1740,1631,262,217,181,173,168,136,
             83,76,65,57,39,126,103,2534,2533,2512,862,7519,7518,7517,7516,7515,7514,7513,7512,7511,7510,7509,7508,
             6992,4551,4550,4542,2621,12466,6996,6993,4590,2303,2294,2285,1025,830,245,233,215,183,6982,4555,142,
             109]

    def __init__(self):
        # 30 秒超时
        socket.setdefaulttimeout(300)

    # 获取主题页源码
    def access_item(self, item, page):
        url = ''
        if page == 1:
            url = MeituluSpider.item_url % item
        else:
            url = MeituluSpider.item_url_next % (item, page)
        req = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(req) as rsp:
                html = rsp.read()
            try:
                html_str = html.decode('utf8')
            except UnicodeDecodeError:
                html_str = gzip.decompress(html).decode('utf8')
        except HTTPError as e:
            html_str = None
        return html_str

    # 解析主题页源码得到图片下载地址
    def parse_item(self, html):
        img_urls = []
        model = ''

        soup = BeautifulSoup(html, 'html.parser')

        # 得到模特名字
        cl = soup.find('div', class_='c_l')
        if cl != None:
            ps = cl.find_all('p')
            if ps != None:
                for p in ps:
                    pc = p.string
                    if pc != None:
                        if pc.find('模特姓名：') != -1:
                            model = pc[5:]
                            break
                    else:
                        pc = p.strings
                        pc_arr = []
                        for tag in pc:
                            pc_arr.append(tag.string)
                        if pc_arr[0].find('模特姓名：') != -1:
                            model = pc_arr[1]

        content = soup.find('div', class_='content')
        if content != None:
            imgs = content.find_all('img')
            if imgs != None:
                for img in imgs:
                    img_url = img.attrs['src']
                    if img_url != None:
                        img_urls.append(img_url)
        return model, img_urls

    def save_img(self, url):
        filename = url.split('/')[-1]

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64)',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'https://www.meitulu.com/'
        }
        if not os.path.exists(filename):
            print('\t\tdownload %s' % url)
            try:
                with open(filename, 'wb') as file:
                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req) as rsp:
                        file.write(rsp.read())
            except Exception as e:
                if os.path.exists(filename):
                    os.remove(filename)
                traceback.print_exc()


if __name__ == '__main__':

    print('start...')

    spider = MeituluSpider()
    for item in MeituluSpider.items:

        model = ''
        img_urls = []
        urls = []

        # 这个目录保存视频文件
        os.chdir('c:\pic')

        print('\tdownload item %d' % item)
        for page in range(1, MeituluSpider.page_max):
            html = spider.access_item(item, page)
            if html == None:
                break
            else:
                print('\t\tparse image urls from item page %d' % page)
                model, img_urls = spider.parse_item(html)
                urls.extend(img_urls)

        size = len(urls)
        if size > 0:
            print('\t\ttotal image count is %d' % size)
            title = model
            title = title.replace('|','_')
            title = title.replace(':', '_')
            title = title.replace('<', '_')
            title = title.replace('"', '_')
            title = title.replace('?', '_')
            title = title.replace('/', '_')
            title = title.replace('\\', '_')
            title = title.replace('*', '_')
            title = title.replace('>', '_')

            path = '%d_%s' % (item, title)
            if not os.path.exists(path):
                os.mkdir(path)
            os.chdir(path)
            for url in urls:
                spider.save_img(url)

    print('done...')
