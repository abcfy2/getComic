#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import getComic
import os
import re
import sys

class TencentComicDownloader(QWidget):
    def __init__(self, parent=None):
        super(TencentComicDownloader, self).__init__(parent)

        nameLabel = QLabel("漫画首页:")

        self.nameLine = QLineEdit()

        self.analysisButton = QPushButton("分析")
        self.analysisButton.clicked.connect(self.anaysisURL)
        self.nameLine.returnPressed.connect(self.analysisButton.click)

        pathLineLabel = QLabel("下载路径:")
        self.pathLine = QLineEdit()
        defaultPath = os.path.join(os.path.expanduser('~'), 'tencent_comic')
        self.pathLine.setText(defaultPath)
        
        self.browseButton = QPushButton("浏览")
        self.browseButton.clicked.connect(self.getPath)

        comicNameLabel = QLabel("漫画名: ")
        self.comicNameLabel = QLabel("暂无")
        
        comicIntroLabel = QLabel("简介: ")
        self.comicIntro = QLabel("暂无")
        self.comicIntro.setWordWrap(True)

        chapterGroupBox = QGroupBox("章节列表:")
        
        self.chapterListView = QListWidget(chapterGroupBox)
        self.chapterListView.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.chapterListView.setEnabled(False)

        groupBoxLayout = QHBoxLayout(chapterGroupBox)
        groupBoxLayout.addWidget(self.chapterListView)

        self.downloadButton = QPushButton("下载选中")
        self.statusLabel = QLabel("输入要下载的漫画的首页，然后点分析")
        self.statusLabel.setWordWrap(True)

        self.downloadButton.setEnabled(False)
        self.downloadButton.clicked.connect(self.download)

        mainLayout = QGridLayout()
        mainLayout.addWidget(nameLabel, 0, 0)
        mainLayout.addWidget(self.nameLine, 0, 1)
        mainLayout.addWidget(self.analysisButton, 0, 2)
        mainLayout.addWidget(pathLineLabel, 1, 0)
        mainLayout.addWidget(self.pathLine, 1, 1)
        mainLayout.addWidget(self.browseButton, 1, 2)
        mainLayout.addWidget(comicNameLabel, 2, 0)
        mainLayout.addWidget(self.comicNameLabel, 2, 1, 1, 2)
        mainLayout.addWidget(comicIntroLabel, 3, 0)
        mainLayout.addWidget(self.comicIntro, 3, 1, 1, 2)
        mainLayout.addWidget(chapterGroupBox, 4, 0, 1, 3)
        mainLayout.addWidget(self.downloadButton, 5, 2)
        mainLayout.addWidget(self.statusLabel, 5, 0, 1, 2)


        self.setLayout(mainLayout)
        self.setWindowTitle("腾讯漫画下载")
        self.setGeometry(400, 300, 800, 500)

    def setStatus(self, status):
        self.statusLabel.setText(status)

    def enableWidget(self, enable):
        self.downloadButton.setEnabled(enable)
        self.nameLine.setEnabled(enable)
        self.pathLine.setEnabled(enable)
        self.chapterListView.setEnabled(enable)
        self.analysisButton.setEnabled(enable)
        self.browseButton.setEnabled(enable)

        if enable:
            self.downloadButton.setText('下载选中')
            self.chapterListView.setFocus()

    def getPath(self):
        path = str(QFileDialog.getExistingDirectory(self, "选择下载目录"))
        if path:
            self.pathLine.setText(path)

    def anaysisURL(self):
        url = self.nameLine.text()

        self.downloadButton.setEnabled(False)
        self.comicNameLabel.setText("暂无")
        self.comicIntro.setText("暂无")
        self.chapterListView.clear()
        self.chapterListView.setEnabled(False)

        try:
            if getComic.isLegelUrl(url):
                self.id = getComic.getId(url)
                self.comicName,self.comicIntrd,self.count,self.contentList = getComic.getContent(self.id)

                self.contentNameList = []
                for item in self.contentList:
                    for k in item:
                        self.contentNameList.append(item[k]['t'])
                
                self.comicNameLabel.setText(self.comicName)
                self.comicIntro.setText(self.comicIntrd)
                self.chapterListView.setEnabled(True)
                self.downloadButton.setEnabled(True)
                self.chapterListView.setFocus()
                self.statusLabel.setText('选择要下载的章节后点击右侧按钮')

                for i in range(len(self.contentNameList)):
                    self.chapterListView.addItem('第{0:0>4}话-{1}'.format(i+1, self.contentNameList[i]))
                    self.chapterListView.item(i).setSelected(True)

                self.downloadButton.setEnabled(True)

            else:
                self.statusLabel.setText('<font color="red">错误的URL格式！请输入正确的漫画首页地址！</font>')

        except getComic.ErrorCode as e:
            if e.code == 2:
                self.statusLabel.setText('<font color="red">无法跳转为移动端URL,请进入http://m.ac.qq.com找到该漫画地址</font>')

        except KeyError:
            self.statusLabel.setText('<font color="red">不存在的地址</font>')

    def download(self):
        self.downloadButton.setText("下载中...")

        self.enableWidget(False)

        selectedChapterList = [ item.row() for item in self.chapterListView.selectedIndexes() ]

        path = self.pathLine.text()
        comicName = self.comicName

        comicPath = os.path.join(path, comicName)

        if not os.path.isdir(path):
            os.makedirs(path)

        if not os.path.isdir(comicPath):
            os.makedirs(comicPath)

        self.downloadThread = Downloader(selectedChapterList, comicPath, self.contentList, self.contentNameList, self.id)
        self.downloadThread.output.connect(self.setStatus)
        self.downloadThread.finished.connect(lambda: self.enableWidget(True))
        self.downloadThread.start()
        
class Downloader(QThread):
    output = pyqtSignal(['QString'])
    finished = pyqtSignal()

    def __init__(self, selectedChapterList, comicPath, contentList, contentNameList, id, parent=None):
        super(Downloader, self).__init__(parent)

        self.selectedChapterList = selectedChapterList
        self.comicPath = comicPath
        self.contentList = contentList
        self.contentNameList = contentNameList
        self.id = id

    def run(self):
        try:
            for i in self.selectedChapterList:
                outputString = '正在下载第{0:0>4}话: {1}...'.format(i+1, self.contentNameList[i])
                print(outputString)
                self.output.emit(outputString)
                contentPath = os.path.join(self.comicPath, '第{0:0>4}话'.format(i+1))
                
                #如果章节名有左右斜杠时，不创建带有章节名的目录，因为这是路径分隔符
                forbiddenRE = re.compile(r'[\\/":*?<>|]') #windows下文件名非法字符\ / : * ? " < > |
                if not forbiddenRE.search(self.contentNameList[i]):
                    contentPath = os.path.join(self.comicPath, '第{0:0>4}话-{1}'.format(i+1, self.contentNameList[i]))

                if not os.path.isdir(contentPath):
                    os.mkdir(contentPath)
                imgList = getComic.getImgList(self.contentList[i], self.id)
                getComic.downloadImg(imgList, contentPath)
                
                self.output.emit('完毕!')
       
        except Exception as e:
            self.output.emit('<font color="red">{}</font>\n'
                    '遇到异常!请尝试重新点击下载按钮重试'.format(e))
            raise

        finally:
            self.finished.emit()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    main = TencentComicDownloader()
    main.show()

    app.exec_()
