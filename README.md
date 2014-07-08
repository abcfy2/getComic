getComic
========

***本代码仅供学习交流使用，严禁用于非法用途，各种PR都欢迎***

下载腾讯漫画的脚本。空参运行进入交互式模式，支持的参数可以加``-h``或``--help``参数查看。

**依赖**:

* python3
* 第三方类库[requests](http://docs.python-requests.org/en/latest/user/install/#install)

ubuntu系列系统使用以下命令安装依赖：

    sudo apt-get update ; sudo apt-get install python3 python3-requests

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

**更新日志**
* 增加-l|--list参数，指定需要下载的章节范围，相关issue: #2
* 2014-07-05更新： CF漫画地址 (http://ac.qq.com/cf) 无法跳转至对应的移动端URL，这一类地址将给出错误提示并退出
* 2014-07-04更新： 加入命令行参数支持功能
* 2014-07-03更新： 伪续传实现，判断目标文件路径存在就跳过下载（腾讯应该加入了防刷机制，无法通过head请求得到的content-length判断究竟是否需要重下，因为for循环+head请求过快，会被ban掉，造成异常退出）
* 2014-07-03更新： 使用ipad的UA，这样访问非id的URL，会跳转为``http://m.ac.qq.com``这样带有id的移动版URL，可以搞定``http://ac.qq.com/naruto``或``http://ac.qq.com/onepiece``这一类非id结尾的URL。

下一步计划：

* ~~实现火影等无id的页面下载~~(已解决)
* ~~实现完整的命令行参数~~(已解决)
* (待定)一个图形界面(可能会用pyqt)
