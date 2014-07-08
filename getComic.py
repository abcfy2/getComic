#!/usr/bin/env python3
# encoding: utf-8

'''***本代码仅供学习交流使用，严禁用于非法用途，各种PR都欢迎***'''

import requests
import re
import json
import os
import argparse

requestSession = requests.session()
UA = 'Mozilla/5.0 (iPad; CPU OS 5_1 like Mac OS X; en-us) \
        AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 \
        Mobile/9B176 Safari/7534.48.3' # ipad UA
requestSession.headers.update({'User-Agent': UA})

def isLegelUrl(url):
    legalUrl1 = re.compile(r'http://ac.qq.com/Comic/comicInfo/id/\d+')
    legalUrl2 = re.compile(r'http://m.ac.qq.com/Comic/comicInfo/id/\d+')
    legalUrl3 = re.compile(r'http://ac.qq.com/\w+')

    if legalUrl1.match(url):
        return True
    elif legalUrl2.match(url):
        return True
    elif legalUrl3.match(url):
        return True
    else:
        return False

def getId(url):
    if not isLegelUrl(url):
        print('请输入正确的url！具体支持的url请在命令行输入-h|--help参数查看帮助文档。')
        exit(1)

    numRE = re.compile(r'\d+$')
    
    if not numRE.search(url):
        get_id_request = requestSession.get(url)
        url = get_id_request.url
        if not isLegelUrl(url):
            print('无法自动跳转移动端URL，请进入http://m.ac.qq.com，找到'
            '该漫画地址。\n'
            '地址应该像这样: '
            'http://m.ac.qq.com/Comic/comicInfo/id/xxxxx (xxxxx为整数)')
            exit(2)
            
    id = numRE.findall(url)[0]
    
    return id    

def getContent(id):
    getComicInfoUrl = 'http://m.ac.qq.com/GetData/getComicInfo?id={}'.format(id)
    getComicInfo = requestSession.get(getComicInfoUrl)
    comicInfoJson = getComicInfo.text
    comicInfo = json.loads(comicInfoJson)
    comicName = comicInfo['title']
    getChapterListUrl = 'http://m.ac.qq.com/GetData/getChapterList?id={}'.format(id)
    getChapterList = requestSession.get(getChapterListUrl)
    contentJson = json.loads(getChapterList.text)
    count = contentJson['length']
    sortedContentList = []
    for i in range(count + 1):
        for item in contentJson:
            if isinstance(contentJson[item], dict) and contentJson[item]['seq'] == i:
                sortedContentList.append({item: contentJson[item]})
                break
    return (comicName, count, sortedContentList)

def getImgList(contentJson, id):
    cid = list(contentJson.keys())[0]
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
        l = [j % 1000 // 100, j % 100, j, k]
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
        print('\r正在下载第{}张图片...'.format(i), end = '')
        imgPath = os.path.join(contentPath, '{0:0>3}.jpg'.format(i))
        i += 1
        
        #目标文件存在就跳过下载
        if os.path.isfile(imgPath):
            continue

        try:
            downloadRequest = requestSession.get(imgUrl, stream=True)
            with open(imgPath, 'wb') as f:
                for chunk in downloadRequest.iter_content(chunk_size=1024): 
                    if chunk: # filter out keep-alive new chunks
                        f.write(chunk)
                        f.flush()
        except (KeyboardInterrupt, SystemExit):
            print('\n\n中断下载，删除未下载完的文件！')
            if os.path.isfile(imgPath):
                os.remove(imgPath)
            exit(3)

    print('完毕!\n')

def parseLIST(lst):
    '''解析命令行中的-l|--list参数，返回解析后的章节列表'''
    legalListRE = re.compile(r'^\d+([,-]\d+)*$')
    if not legalListRE.match(lst):
        raise LISTFormatError(lst + ' 不匹配正则: ' + r'^\d+([,-]\d+)*$')

    #先逗号分割字符串，分割后的字符串再用短横杠分割
    parsedLIST = []
    sublist = lst.split(',')
    numRE = re.compile('^\d+$')

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
            else:
                print('警告: 参数中包括不存在的章节0，自动忽略')
            parsedLIST.extend(range(minnum, maxnum+1))

    parsedLIST = sorted(set(parsedLIST)) #按照从小到大的顺序排序并去重
    return parsedLIST

def main(url, path, lst=None):
    '''url: 要爬取的漫画首页。 path: 漫画下载路径。 lst: 要下载的章节列表'''
    #url = 'http://ac.qq.com/Comic/comicInfo/id/511915'
    #url = 'http://m.ac.qq.com/Comic/comicInfo/id/505430'
    #url = 'http://ac.qq.com/Comic/ComicInfo/id/512742'
    #url = 'http://m.ac.qq.com/Comic/comicInfo/id/511915'
    #url = 'http://ac.qq.com/naruto'
    #url = 'http://ac.qq.com/onepiece'
    #url = 'http://ac.qq.com/dragonball'
    #url = 'http://ac.qq.com/Comic/comicInfo/id/8777'
    #url = 'http://ac.qq.com/Comic/comicInfo/id/518333'   #要爬取的漫画首页
    if not os.path.isdir(path):
       os.makedirs(path)
    id = getId(url)
    comicName,count,contentList = getContent(id)
    contentNameList = []
    for item in contentList:
        for k in item:
            contentNameList.append(item[k]['t'])
    print('漫画名: {}'.format(comicName))
    print('章节数: {}'.format(count))
    print('章节列表:')
    try:
        print('\n'.join(contentNameList))
    except Exception:
        print('章节列表包含无法解析的特殊字符\n')
    comicPath = os.path.join(path, comicName)
    if not os.path.isdir(comicPath):
        os.mkdir(comicPath)
    print()
    
    if not lst:
        contentRange = range(1, len(contentList))
    else:
        contentRange = parseLIST(lst)

    for i in contentRange:
        if i > len(contentList):
            print('警告: 章节总数 {} ,'
                    '参数中包含过大数值,'
                    '自动忽略'.format(len(contentList)))
            break

        contentPath = os.path.join(comicPath, '第{0:0>4}话'.format(i))

        try:
            print('正在下载第{0:0>4}话: {1}'.format(i, contentNameList[i -1]))
            #如果章节名有左右斜杠时，不创建带有章节名的目录，因为这是路径分隔符
            forbiddenRE = re.compile(r'[\\/":*?<>|]') #windows下文件名非法字符\ / : * ? " < > |
            if not forbiddenRE.search(contentNameList[i - 1]):
                contentPath = os.path.join(comicPath, '第{0:0>4}话-{1}'.format(i, contentNameList[i - 1]))
        except Exception:
            print('正在下载第{0:0>4}话: {1}'.format(i))

        if not os.path.isdir(contentPath):
            os.mkdir(contentPath)

        imgList = getImgList(contentList[i - 1], id)
        downloadImg(imgList, contentPath)
    
if __name__ == '__main__':
    defaultPath = os.path.expanduser('~/tencent_comic')

    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
                                     description='*下载腾讯漫画，仅供学习交流，请勿用于非法用途*\n'
                                     '空参运行进入交互式模式运行。')
    parser.add_argument('-u', '--url', help='要下载的漫画的首页，可以下载以下类型的url: \n'
            'http://ac.qq.com/Comic/comicInfo/id/511915\n'
            'http://m.ac.qq.com/Comic/comicInfo/id/505430\n'
            'http://ac.qq.com/naruto')
    parser.add_argument('-p', '--path', help='漫画下载路径。 默认: {}'.format(defaultPath), 
                default=defaultPath)
    parser.add_argument('-l', '--list', help=("要下载的漫画章节列表，不指定则下载所有章节。格式范例: \n"
                                              "N - 下载具体某一章节，如-l 1, 下载第1章\n"
                                              'N,N... - 下载某几个不连续的章节，如 "-l 1,3,5", 下载1,3,5章\n'
                                              'N-N... - 下载某一段连续的章节，如 "-l 10-50", 下载[10,50]章\n'
                                              '杂合型 - 结合上面所有的规则，如 "-l 1,3,5-7,11-111"'))
    args = parser.parse_args()
    url = args.url
    path = args.path
    lst = args.list

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

    main(url, path, lst)
