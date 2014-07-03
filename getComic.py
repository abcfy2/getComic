#!/usr/bin/env python3
# encoding: utf-8

'''***本代码仅供学习交流使用，严禁用于非法用途，各种PR都欢迎***'''

import requests
import re
import json
import os


requestSession = requests.session()
UA = 'Mozilla/5.0 (iPad; CPU OS 5_1 like Mac OS X; en-us) \
        AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 \
        Mobile/9B176 Safari/7534.48.3' # ipad UA
requestSession.headers.update({'User-Agent': UA})

def getId(url):
    numRE = re.compile(r'\d+$')
    if not numRE.search(url):
        get_id_request = requestSession.get(url)
        url = get_id_request.url
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
        
        #判断是否需要重新下载
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
            exit(1)

    print('完毕!\n')

def main():
    #url = 'http://ac.qq.com/Comic/comicInfo/id/511915'
    #url = 'http://m.ac.qq.com/Comic/comicInfo/id/505430'
    #url = 'http://ac.qq.com/Comic/ComicInfo/id/512742'
    #url = 'http://m.ac.qq.com/Comic/comicInfo/id/511915'
    #url = 'http://ac.qq.com/naruto'
    #url = 'http://ac.qq.com/onepiece'
    url = 'http://ac.qq.com/dragonball'
    #url = 'http://ac.qq.com/Comic/comicInfo/id/518333'   #要爬取的漫画首页
    path = 'C:\\Users\\FJP\\Desktop'
    #path = '/home/fengyu'  #下载图片存放路径
    if not os.path.isdir(path):
       os.mkdir(path)
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
    i = 0
    for content in contentList:
        contentPath = os.path.join(comicPath, '第{0:0>4}话'.format(i + 1))
        try:
            print('正在下载第{0:0>4}话: {1}'.format(i + 1, contentNameList[i]))
            #如果章节名有左右斜杠时，不创建带有章节名的目录，因为这是路径分隔符
            forbiddenRE = re.compile(r'[\\/":*?<>|]') #windows下文件名非法字符\ / : * ? " < > |
            if not forbiddenRE.search(contentNameList[i]):
                contentPath = os.path.join(comicPath, '第{0:0>4}话-{1}'.format(i + 1, contentNameList[i]))
        except Exception:
            print('正在下载第{0:0>4}话: {1}'.format(i + 1))
        if not os.path.isdir(contentPath):
            os.mkdir(contentPath)
        imgList = getImgList(content, id)
        downloadImg(imgList, contentPath)
        i += 1
    
if __name__ == '__main__':
    main()
