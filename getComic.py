#!/usr/bin/env python3
# encoding: utf-8

import requests
from lxml import html
import base64
import re
import json

#url = 'http://ac.qq.com/Comic/comicInfo/id/511915'
url = 'http://ac.qq.com/Comic/ComicInfo/id/17114'
requestSession = requests.session()

def getContent(url):
    homePage = requestSession.get(url)
    tree = html.fromstring(homePage.text)
    contentURL = tree.xpath('/html/body/div/div/ol/li/p/span/a/@href')
    contentURL = [ 'http://ac.qq.com' + url for url in contentURL ]
    contentName = tree.xpath('/html/body/div/div/ol/li/p/span/a/text()')
    return (contentURL,contentName)

def getImgList(url):
    numRE = re.compile(r'\d+')
    id, cid = numRE.findall(url)
    reqApiURL = 'http://m.ac.qq.com/View/mGetPicHash?id={}&cid={}'.format(id, cid)
    imgJson = requestSession.get(reqApiURL).text
    print(imgJson)

if __name__ == '__main__':
    contentURL,contentName = getContent(url)
    print('页面链接：')
    print(contentURL)
    print('标题：')
    print(contentName)
    getImgList(contentURL[0])
