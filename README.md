getComic
========

***本代码仅供学习交流使用，严禁用于非法用途，各种PR都欢迎***

下载腾讯漫画的脚本。脚本暂未完成，README暂时未写完。目前将要下载的漫画首页写入脚本执行即可。

**依赖**:

* python3
* 第三方类库[requests](http://docs.python-requests.org/en/latest/user/install/#install)

ubuntu系列系统使用以下命令安装依赖：

    sudo apt-get update ; sudo apt-get install python3 python3-requests

URL格式: 漫画首页的URL，如``http://m.ac.qq.com/Comic/view/id/518333``(移动版) 或 ``http://ac.qq.com/Comic/comicInfo/id/17114``(PC版)。即有数字id的。

2014-07-03更新： 使用ipad的UA，这样访问非id的URL，会跳转为``http://m.ac.qq.com``这样带有id的移动版URL，可以搞定``http://ac.qq.com/naruto``或``http://ac.qq.com/onepiece``这一类非id结尾的URL。

下一步计划：

* ~~实现火影等无id的页面下载~~(已解决)
* 实现完整的命令行参数
* (待定)一个图形界面(可能会用pyqt)
