#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function
from __future__ import unicode_literals
import requests
from lxml import html
import base64
import re
import json
import os

#url = 'http://ac.qq.com/Comic/comicInfo/id/511915'
#url = 'http://ac.qq.com/Comic/ComicInfo/id/17114'
url = 'http://ac.qq.com/Comic/comicInfo/id/518333'   #要爬取的漫画首页
#path = 'C:\\Users\\FJP\\Desktop'
path = '/home/fengyu'  #下载图片存放路径
if not os.path.isdir(path):
    os.mkdir(path)
requestSession = requests.session()

def getContent(url):
    homePage = requestSession.get(url)
    tree = html.fromstring(homePage.text)
    contentURL = tree.xpath('/html/body/div/div/ol/li/p/span/a/@href')
    contentURL = [ 'http://ac.qq.com' + url for url in contentURL ]
    comicName = tree.xpath('/html/body/div[3]/div[1]/div[1]/div[2]/div[1]/div[1]/h2/strong/text()')
    contentName = tree.xpath('/html/body/div/div/ol/li/p/span/a/text()')
    return (comicName[0],contentName,contentURL)

def getImgList(url):
    numRE = re.compile(r'\d+')
    id, cid = numRE.findall(url)
    getPicHashURL = 'http://m.ac.qq.com/View/mGetPicHash?id={}&cid={}'.format(id, cid)
    picJsonPage = requestSession.get(getPicHashURL).text
    picJson = json.loads(picJsonPage)
    count = picJson['pCount']    #统计图片数量
    pHash = picJson['pHash']
    sortedImgDictList = []
    for i in range(1, count + 1):
        for item in pHash:
            if pHash[item]['seq'] == i:
                sortedImgDictList.append(pHash[item])
                break
    imgList = []
    for imgDict in sortedImgDictList:
        k = imgDict['cid']
        m = imgDict['pid']
        j = int(id)
        uin = max(j + k + m, 10001)
        l = [j % 1000 / 100, j % 100, j, k]
        n = '/mif800/' + '/'.join(str(j) for j in l) + '/'
        h = str(m) + '.mif2'
        g="http://ac.tc.qq.com/store_file_download?buid=15017&uin="+str(uin)+"&dir_path="+n+"&name="+h
        imgList.append(g)
    return imgList

def downloadImg(imgUrlList, contentPath):
    count = len(imgUrlList)
    print('该集漫画共计{}张图片'.format(count))
    i = 1
    for imgUrl in imgUrlList:
        print('正在下载第{}张图片...'.format(i), end='')
        imgPath = os.path.join(contentPath, '{0:0>3}.jpg'.format(i))
        downloadRequest = requestSession.get(imgUrl, stream=True)
        with open(imgPath, 'wb') as f:
            for chunk in downloadRequest.iter_content(chunk_size=1024): 
                if chunk: # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
        i += 1
        print('完毕!')
    print('\n')

def main():
    comicName,contentName,contentURL = getContent(url)
    print('漫画名: ' + comicName)
    comicPath = os.path.join(path, comicName)
    if not os.path.isdir(comicPath):
        os.mkdir(comicPath)
    print('章节列表: ')
    print('\n'.join(contentName))
    i = 0
    print()
    for content in contentName:
        print('正在下载章节: {} ...'.format(content))
        contentPath = os.path.join(comicPath, '{0:0>4}{1}'.format(i, content))
        if not os.path.isdir(contentPath):
            os.mkdir(contentPath)
        imgList = getImgList(contentURL[i])
        downloadImg(imgList, contentPath)
        i += 1
    
if __name__ == '__main__':
    main()
