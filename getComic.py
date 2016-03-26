#!/usr/bin/env python3
# encoding: utf-8

'''***本代码仅供学习交流使用，严禁用于非法用途，各种PR都欢迎***'''

import requests
import re
import json
import os
import sys
import argparse
import threading
from time import sleep

requestSession = requests.session()
UA = 'Mozilla/5.0 (Linux; U; Android 4.0.3; zh-CN; \
HTC Velocity 4G X710s Build/IML74K) AppleWebKit/534.30 \
(KHTML, like Gecko) Version/4.0 UCBrowser/10.1.3.546 \
U3/0.8.0 Mobile Safari/534.30' # UC UA
requestSession.headers.update({'User-Agent': UA})

class ErrorCode(Exception):
    '''自定义错误码:
        1: URL不正确
        2: URL无法跳转为移动端URL
        3: 中断下载'''
    def __init__(self, code):
        self.code = code

    def __str__(self):
        return repr(self.code)

def isLegelUrl(url):
    legal_url_list = [
        re.compile(r'^http://ac.qq.com/Comic/[Cc]omicInfo/id/\d+/?$'),
        re.compile(r'^http://m.ac.qq.com/Comic/[Cc]omicInfo/id/\d+/?$'),
        re.compile(r'^http://m.ac.qq.com/comic/index/id/\d+/?$'),
        re.compile(r'^http://ac.qq.com/\w+/?$'),
    ]

    for legal_url in legal_url_list:
        if legal_url.match(url):
            return True
    return False

def getId(url):
    if not isLegelUrl(url):
        print('请输入正确的url！具体支持的url请在命令行输入-h|--help参数查看帮助文档。')
        raise ErrorCode(1)

    numRE = re.compile(r'\d+$')
    
    id = numRE.findall(url)
    if not id:
        get_id_request = requestSession.get(url)
        url = get_id_request.url
        id = numRE.findall(url)
        if not isLegelUrl(url) or not id:
            print('无法自动跳转移动端URL，请进入http://m.ac.qq.com，找到'
            '该漫画地址。\n'
            '地址应该像这样: '
            'http://m.ac.qq.com/Comic/comicInfo/id/xxxxx (xxxxx为整数)')
            raise ErrorCode(2)

    return id[0]

def getContent(id):
    getComicInfoUrl = 'http://m.ac.qq.com/GetData/getComicInfo?id={}'.format(id)
    requestSession.cookies.update({'ac_refer': 'http://m.ac.qq.com'})
    requestSession.headers.update({'Referer': 'http://m.ac.qq.com/Comic/view/id/{}/cid/1'.format(id)})
    getComicInfo = requestSession.get(getComicInfoUrl)
    comicInfoJson = getComicInfo.text
    comicInfo = json.loads(comicInfoJson)
    comicName = comicInfo['title']
    comicIntrd = comicInfo['brief_intrd']
    getChapterListUrl = 'http://m.ac.qq.com/GetData/getChapterList?id={}'.format(id)
    getChapterList = requestSession.get(getChapterListUrl)
    contentJson = json.loads(getChapterList.text)
    count = contentJson['length']
    sortedContentList = []
    for i in range(count + 1):
        for item in contentJson:
            if isinstance(contentJson[item], dict) and contentJson[item].get('seq') == i:
                sortedContentList.append({item: contentJson[item]})
                break
    return (comicName, comicIntrd, count, sortedContentList)

def getImgList(contentJson, comic_id):
    cid = list(contentJson.keys())[0]
    cid_page = requestSession.get('http://m.ac.qq.com/chapter/index/id/{0}/cid/{1}'.format(comic_id, cid)).text
    base64data = re.findall(r"data:\s*'(.+?)'", cid_page)[0][1:]
    img_detail_json = json.loads(__decode_base64_data(base64data))
    imgList = []
    for img_url in img_detail_json.get('picture'):
        imgList.append(img_url['url'])
    return imgList

def __decode_base64_data(base64data):
    base64DecodeChars = [- 1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, -1, 62, -1, -1, -1, 63, 52, 53, 54, 55, 56, 57, 58, 59, 60, 61, -1, -1, -1, -1, -1, -1, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, -1, -1, -1, -1, -1, -1, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, -1, -1, -1, -1, -1]
    data_length = len(base64data)
    i = 0
    out = ""
    c1 = c2 = c3 = c4 = 0
    while i < data_length:
        while True:
            c1 = base64DecodeChars[ord(base64data[i]) & 255]
            i += 1
            if not (i < data_length and c1 == -1):
                break
        if c1 == -1:
            break
        while True:
            c2 = base64DecodeChars[ord(base64data[i]) & 255]
            i += 1
            if not (i < data_length and c2 == -1):
                break
        if c2 == -1:
            break
        out += chr(c1 << 2 | (c2 & 48) >> 4)
        while True:
            c3 = ord(base64data[i]) & 255
            i += 1
            if c3 == 61:
                return out
            c3 = base64DecodeChars[c3]
            if not (i < data_length and c3 == - 1):
                break
        if c3 == -1:
            break
        out += chr((c2 & 15) << 4 | (c3 & 60) >> 2)
        while True:
            c4 = ord(base64data[i]) & 255
            i += 1
            if c4 == 61:
                return out
            c4 = base64DecodeChars[c4]
            if not (i < data_length and c4 == - 1):
                break
        out += chr((c3 & 3) << 6 | c4)
    return out


def downloadImg(imgUrlList, contentPath, one_folder=False):
    count = len(imgUrlList)
    print('该集漫画共计{}张图片'.format(count))
    i = 1
    downloaded_num = 0
    
    def __download_callback():
        nonlocal downloaded_num
        nonlocal count
        downloaded_num += 1
        print('\r{}/{}... '.format(downloaded_num, count), end='')
        
    download_threads = []
    for imgUrl in imgUrlList:
        if not one_folder:
            imgPath = os.path.join(contentPath, '{0:0>3}.jpg'.format(i))
        else:
            imgPath = contentPath + '{0:0>3}.jpg'.format(i)
        i += 1
        
        #目标文件存在就跳过下载
        if os.path.isfile(imgPath):
            count -= 1
            continue
        download_thread = threading.Thread(target=__download_one_img, 
            args=(imgUrl,imgPath, __download_callback))
        download_threads.append(download_thread)
        download_thread.start()
    [ t.join() for t in download_threads ]
    print('完毕!\n')

def __download_one_img(imgUrl,imgPath, callback):
    retry_num = 0
    retry_max = 2
    while True:
      try:
          downloadRequest = requestSession.get(imgUrl, stream=True)
          with open(imgPath, 'wb') as f:
              for chunk in downloadRequest.iter_content(chunk_size=1024): 
                  if chunk: # filter out keep-alive new chunks
                      f.write(chunk)
                      f.flush()
          callback()
          break
      except (KeyboardInterrupt, SystemExit):
          print('\n\n中断下载，删除未下载完的文件！')
          if os.path.isfile(imgPath):
              os.remove(imgPath)
          raise ErrorCode(3)
      except:
          retry_num += 1
          if retry_num >= retry_max:
              raise
          print('下载失败，重试' + str(retry_num) + '次')
          sleep(2)

def parseLIST(lst):
    '''解析命令行中的-l|--list参数，返回解析后的章节列表'''
    legalListRE = re.compile(r'^\d+([,-]\d+)*$')
    if not legalListRE.match(lst):
        raise LISTFormatError(lst + ' 不匹配正则: ' + r'^\d+([,-]\d+)*$')

    #先逗号分割字符串，分割后的字符串再用短横杠分割
    parsedLIST = []
    sublist = lst.split(',')
    numRE = re.compile(r'^\d+$')

    for sub in sublist:
        if numRE.match(sub):
            if int(sub) > 0: #自动忽略掉数字0
                parsedLIST.append(int(sub))
            else:
                print('警告: 参数中包括不存在的章节0，自动忽略')
        else:
            splitnum = list(map(int, sub.split('-')))
            maxnum = max(splitnum)
            minnum = min(splitnum)       #min-max或max-min都支持
            if minnum == 0:
                minnum = 1               #忽略数字0
                print('警告: 参数中包括不存在的章节0，自动忽略')
            parsedLIST.extend(range(minnum, maxnum+1))

    parsedLIST = sorted(set(parsedLIST)) #按照从小到大的顺序排序并去重
    return parsedLIST

def main(url, path, lst=None, one_folder=False):
    '''url: 要爬取的漫画首页。 path: 漫画下载路径。 lst: 要下载的章节列表(-l|--list后面的参数)'''
    try:
        if not os.path.isdir(path):
           os.makedirs(path)
        id = getId(url)
        comicName,comicIntrd,count,contentList = getContent(id)
        contentNameList = []
        for item in contentList:
            for k in item:
                contentNameList.append(item[k]['t'])
        print('漫画名: {}'.format(comicName))
        print('简介: {}'.format(comicIntrd))
        print('章节数: {}'.format(count))
        print('章节列表:')
        try:
            print('\n'.join(contentNameList))
        except Exception:
            print('章节列表包含无法解析的特殊字符\n')
            
        forbiddenRE = re.compile(r'[\\/":*?<>|]') #windows下文件名非法字符\ / : * ? " < > |
        comicName = re.sub(forbiddenRE, '_', comicName) #将windows下的非法字符一律替换为_
        comicPath = os.path.join(path, comicName)
        if not os.path.isdir(comicPath):
            os.makedirs(comicPath)
        print()
        
        if not lst:
            contentRange = range(1, len(contentList) + 1)
        else:
            contentRange = parseLIST(lst)

        for i in contentRange:
            if i > len(contentList):
                print('警告: 章节总数 {} ,'
                        '参数中包含过大数值,'
                        '自动忽略'.format(len(contentList)))
                break

            contentNameList[i - 1] = re.sub(forbiddenRE, '_', contentNameList[i - 1]) #将windows下的非法字符一律替换为_
            contentPath = os.path.join(comicPath, '第{0:0>4}话-{1}'.format(i, contentNameList[i - 1]))

            try:
                print('正在下载第{0:0>4}话: {1}'.format(i, contentNameList[i -1]))
            except Exception:
                print('正在下载第{0:0>4}话: {1}'.format(i))

            if not one_folder:
                if not os.path.isdir(contentPath):
                    os.mkdir(contentPath)

            imgList = getImgList(contentList[i - 1], id)
            downloadImg(imgList, contentPath, one_folder)

    except ErrorCode as e:
        exit(e.code)
    
if __name__ == '__main__':
    defaultPath = os.path.join(os.path.expanduser('~'), 'tencent_comic')

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description='*下载腾讯漫画，仅供学习交流，请勿用于非法用途*\n'
                                     '空参运行进入交互式模式运行。')
    parser.add_argument('-u', '--url', help='要下载的漫画的首页，可以下载以下类型的url: \n'
            'http://ac.qq.com/Comic/comicInfo/id/511915\n'
            'http://m.ac.qq.com/Comic/comicInfo/id/505430\n'
            'http://pad.ac.qq.com/Comic/comicInfo/id/505430\n'
            'http://ac.qq.com/naruto')
    parser.add_argument('-p', '--path', help='漫画下载路径。 默认: {}'.format(defaultPath), 
                default=defaultPath)
    parser.add_argument('-d', '--dir', action='store_true', help='将所有图片下载到一个目录(适合腾讯漫画等软件连看使用)')
    parser.add_argument('-l', '--list', help=("要下载的漫画章节列表，不指定则下载所有章节。格式范例: \n"
                                              "N - 下载具体某一章节，如-l 1, 下载第1章\n"
                                              'N,N... - 下载某几个不连续的章节，如 "-l 1,3,5", 下载1,3,5章\n'
                                              'N-N... - 下载某一段连续的章节，如 "-l 10-50", 下载[10,50]章\n'
                                              '杂合型 - 结合上面所有的规则，如 "-l 1,3,5-7,11-111"'))
    args = parser.parse_args()
    url = args.url
    path = args.path
    lst = args.list
    one_folder = args.dir

    if lst:
        legalListRE = re.compile(r'^\d+([,-]\d+)*$')
        if not legalListRE.match(lst):
            print('LIST参数不合法，请参考--help键入合法参数！')
            exit(1)

    if not url:
        url = input('请输入漫画首页地址: ')
        path = input('请输入漫画保存路径(默认: {}): '.format(defaultPath))
        if not path:
            path = defaultPath

    main(url, path, lst, one_folder)
