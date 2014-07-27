getComic
========

***本代码仅供学习交流使用，严禁用于非法用途，各种PR都欢迎***

下载腾讯漫画的脚本。空参运行进入交互式模式，支持的参数可以加``-h``或``--help``参数查看。

**GUI版本提供windows下打包好的版本**

[点此下载](http://bcs.duapp.com/myownstore/getcomic-pack.7z?response-cache-control=private) <--点开如遇BAE抽风(该页无法显示)，尝试右键另存为或用下载工具下载

使用[cx\_freeze](http://cx-freeze.sourceforge.net/)打包

**依赖**:

* python3
* 第三方类库[requests](http://docs.python-requests.org/en/latest/user/install/#install)
* [python3-pyqt5](http://www.riverbankcomputing.co.uk/software/pyqt/download5) (GUI依赖，不用GUI可不装)

ubuntu系列系统使用以下命令安装依赖：

    sudo apt-get update ; sudo apt-get install python3 python3-requests
    sudo apt-get install python3-pyqt5 #GUI依赖，不用GUI可不装

URL格式: 漫画首页的URL，如``http://m.ac.qq.com/Comic/view/id/518333``(移动版) 或 ``http://ac.qq.com/Comic/comicInfo/id/17114``, ``http://ac.qq.com/naruto``(PC版)

**命令行帮助**

```bash
./getComic.py -h
usage: getComic.py [-h] [-u URL] [-p PATH] [-l LIST]

*下载腾讯漫画，仅供学习交流，请勿用于非法用途*
空参运行进入交互式模式运行。

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     要下载的漫画的首页，可以下载以下类型的url: 
                        http://ac.qq.com/Comic/comicInfo/id/511915
                        http://m.ac.qq.com/Comic/comicInfo/id/505430
                        http://ac.qq.com/naruto
  -p PATH, --path PATH  漫画下载路径。 默认: /home/fengyu/tencent_comic
  -l LIST, --list LIST  要下载的漫画章节列表，不指定则下载所有章节。格式范例: 
                        N - 下载具体某一章节，如-l 1, 下载第1章
                        N,N... - 下载某几个不连续的章节，如 "-l 1,3,5", 下载1,3,5章
                        N-N... - 下载某一段连续的章节，如 "-l 10-50", 下载[10,50]章
                        杂合型 - 结合上面所有的规则，如 "-l 1,3,5-7,11-111"
```

**GUI预览效果**

支持不连续的章节选择下载

windows预览效果：

![](http://static.oschina.net/uploads/space/2014/0724/222236_2rb7_1395553.jpg)
![](http://static.oschina.net/uploads/space/2014/0724/222329_Pife_1395553.jpg)

deepin/Linux 预览效果：

![](http://static.oschina.net/uploads/space/2014/0724/223412_4Hz4_1395553.jpg)

**更新日志**
* 2014-07-26更新： GUI小细节优化——下载完毕后重新聚焦listview。默认下载路径分隔符windows和linux统一风格
* 2014-07-24更新： 完成GUI界面基本功能
* 2014-07-11更新： 开坑，GUI走起！提交一个基本框架，使用python3-pyqt5的GUI框架。此次递交文件： https://github.com/abcfy2/getComic/commit/6110571122f923a398604ca7faff18615c961683
* 2014-07-08更新： 增加-l|--list参数，指定需要下载的章节范围，相关issue: [#2](https://github.com/abcfy2/getComic/issues/2)
* 2014-07-05更新： CF漫画地址 (http://ac.qq.com/cf) 无法跳转至对应的移动端URL，这一类地址将给出错误提示并退出
* 2014-07-04更新： 加入命令行参数支持功能
* 2014-07-03更新： 伪续传实现，判断目标文件路径存在就跳过下载（腾讯应该加入了防刷机制，无法通过head请求得到的content-length判断究竟是否需要重下，因为for循环+head请求过快，会被ban掉，造成异常退出）
* 2014-07-03更新： 使用ipad的UA，这样访问非id的URL，会跳转为``http://m.ac.qq.com``这样带有id的移动版URL，可以搞定``http://ac.qq.com/naruto``或``http://ac.qq.com/onepiece``这一类非id结尾的URL。

下一步计划：

* ~~实现火影等无id的页面下载~~(已解决)
* ~~实现完整的命令行参数~~(已解决)
* ~~一个图形界面(pyqt5实现)~~
