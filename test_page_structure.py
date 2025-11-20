#!/usr/bin/env python3
# encoding: utf-8

import requests
from lxml import html
import re
import json

def test_with_requests():
    """使用requests测试漫画主页结构"""
    url = 'http://ac.qq.com/Comic/comicInfo/id/511915'  # 中国惊奇先生
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'
    }
    
    print("=== 使用requests测试漫画主页 ===")
    try:
        response = requests.get(url, headers=headers)
        print(f"状态码: {response.status_code}")
        
        # 检查页面内容
        tree = html.fromstring(response.text)
        
        # 查找可能的章节列表
        chapter_selectors = [
            '//*[@id="chapter"]/div[2]/ol[1]/li/p/span/a',
            '//ol[@id="chapter"]//a',
            '//ul[contains(@class, "chapter-list")]//a',
            '//div[contains(@class, "chapter")]//a',
            '//div[contains(@class, "mod_booklist")]//a',
            '//ul[contains(@class, "list")]//a',
            '//div[contains(@class, "works-chapter-list")]//a',
            '//ul[contains(@class, "chapter-list-ul")]//a'
        ]
        
        print("\n=== 章节列表测试 ===")
        for i, selector in enumerate(chapter_selectors):
            try:
                elements = tree.xpath(selector)
                print(f"选择器 {i+1}: 找到 {len(elements)} 个元素")
                if elements:
                    for j, elem in enumerate(elements[:3]):  # 只显示前3个
                        print(f"  - {j+1}: {elem.text.strip() if elem.text else '无文本'} -> {elem.get('href')}")
                    break
            except Exception as e:
                print(f"选择器 {i+1} 失败: {e}")
        
        # 查找漫画名称
        name_selectors = [
            '//*[@id="special_bg"]/div[3]/div[1]/div[1]/div[2]/div[1]/div[1]/h2/strong/text()',
            '//h1[@class="works-intro-title ui-left"]/text()',
            '//h1[@class="detail-main-title"]/text()',
            '//title/text()',
            '//div[@class="works-intro"]/h2/text()',
            '//div[@class="detail-main-hd"]/h1/text()',
            '//div[@class="works-title"]/text()',
            '//h2[@class="works-subtitle"]/text()'
        ]
        
        print("\n=== 漫画名称测试 ===")
        for i, selector in enumerate(name_selectors):
            try:
                elements = tree.xpath(selector)
                if elements:
                    print(f"选择器 {i+1}: {elements[0].strip()}")
                    break
            except Exception as e:
                print(f"选择器 {i+1} 失败: {e}")
        
        # 查找页面中的JSON数据
        print("\n=== JSON数据测试 ===")
        json_patterns = [
            r'window\.DATA\s*=\s*({.*?});',
            r'window\.data\s*=\s*({.*?});',
            r'var\s+DATA\s*=\s*({.*?});',
            r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
            r'window\.comicInfo\s*=\s*({.*?});'
        ]
        
        for pattern in json_patterns:
            matches = re.findall(pattern, response.text)
            if matches:
                print(f"找到JSON数据: {pattern}")
                try:
                    data = json.loads(matches[0])
                    print(f"数据类型: {type(data)}")
                    print(f"键: {data.keys() if isinstance(data, dict) else '不是字典'}")
                except:
                    print("JSON解析失败")
                break
        
        return response.text
        
    except Exception as e:
        print(f"requests测试失败: {e}")
        return None

def test_chapter_page_with_requests():
    """使用requests测试章节页面"""
    chapter_url = 'http://ac.qq.com/ComicView/index/id/511915/cid/1'  # 中国惊奇先生第1话
    
    print("\n=== 使用requests测试章节页面 ===")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36'
    }
    
    try:
        print(f"访问章节页面: {chapter_url}")
        response = requests.get(chapter_url, headers=headers)
        print(f"状态码: {response.status_code}")
        
        # 查找页面中的JavaScript变量
        print("\n=== 查找JavaScript数据 ===")
        js_data_patterns = [
            r'window\.DATA\s*=\s*({.*?});',
            r'window\.data\s*=\s*({.*?});',
            r'var\s+DATA\s*=\s*({.*?});',
            r'window\.__INITIAL_STATE__\s*=\s*({.*?});',
            r'window\.comicInfo\s*=\s*({.*?});'
        ]
        
        for pattern in js_data_patterns:
            matches = re.findall(pattern, response.text)
            if matches:
                print(f"找到JS数据: {pattern}")
                try:
                    data = json.loads(matches[0])
                    print(f"数据类型: {type(data)}")
                    if isinstance(data, dict):
                        print(f"键: {list(data.keys())}")
                        if 'picture' in data:
                            print(f"图片数量: {len(data['picture'])}")
                            for i, img in enumerate(data['picture'][:10]):  # 显示前10张
                                if isinstance(img, dict) and 'url' in img:
                                    print(f"  - {i+1}: {img['url']}")
                                elif isinstance(img, str):
                                    print(f"  - {i+1}: {img}")
                        elif 'pics' in data:
                            print(f"图片数量: {len(data['pics'])}")
                            for i, img in enumerate(data['pics'][:10]):  # 显示前10张
                                if isinstance(img, dict) and 'url' in img:
                                    print(f"  - {i+1}: {img['url']}")
                                elif isinstance(img, str):
                                    print(f"  - {i+1}: {img}")
                except Exception as e:
                    print(f"JSON解析失败: {e}")
                break
        
        # 查找页面源码中的图片URL
        print("\n=== 页面源码中的图片URL ===")
        # 修复正则表达式，避免括号不匹配
        img_url_pattern = r'https?://[^"]*manhua[^"]*\.(?:jpg|jpeg|png|gif|webp)[^"]*'
        img_urls = re.findall(img_url_pattern, response.text)
        print(f"找到 {len(img_urls)} 个图片URL")
        for i, url in enumerate(img_urls[:20]):  # 显示前20个
            print(f"  - {i+1}: {url}")
        
        # 查找可能的图片数据结构
        print("\n=== 查找图片数据结构 ===")
        # 尝试查找包含图片数组的数据结构
        picture_patterns = [
            r'"picture"\s*:\s*\[([^{]*\{[^}]*\}[^]]*)\]',  # picture数组
            r'"picture"\s*:\s*({.*?})',  # picture对象
            r'"pics"\s*:\s*\[([^{]*\{[^}]*\}[^]]*)\]',  # pics数组
            r'"pics"\s*:\s*({.*?})',  # pics对象
        ]
        
        for pattern in picture_patterns:
            matches = re.findall(pattern, response.text)
            if matches:
                print(f"找到图片数据结构: {pattern}")
                print(f"匹配数量: {len(matches)}")
                for i, match in enumerate(matches[:3]):  # 显示前3个
                    print(f"  - {i+1}: {match[:200]}...")
                break
        
        # 查找旧的data和nonce数据
        print("\n=== 查找旧的data和nonce数据 ===")
        data_pattern = r"data:\s*'([^']+)'"
        nonce_pattern = r'data-mpmvr="([^"]+)"'
        
        data_matches = re.findall(data_pattern, response.text)
        nonce_matches = re.findall(nonce_pattern, response.text)
        
        print(f"找到data: {len(data_matches)} 个")
        print(f"找到nonce: {len(nonce_matches)} 个")
        
        if data_matches and nonce_matches:
            print("存在旧的加密数据格式")
        
        return response.text
        
    except Exception as e:
        print(f"章节页面测试失败: {e}")
        return None

def main():
    print("开始测试腾讯漫画页面结构...")
    
    # 测试漫画主页
    test_with_requests()
    
    # 测试章节页面
    test_chapter_page_with_requests()

if __name__ == '__main__':
    main()