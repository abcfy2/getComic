#!/usr/bin/env python3

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import getComic
import os

class TencentComicDownloader(QWidget):
    def __init__(self, parent=None):
        super(TencentComicDownloader, self).__init__(parent)

        nameLabel = QLabel("漫画首页:")
        self.nameLine = QLineEdit()

        self.analysisButton = QPushButton("分析")
        self.analysisButton.clicked.connect(self.anaysisURL)

        pathLineLabel = QLabel("下载路径:")
        self.pathLine = QLineEdit()
        defaultPath = os.path.expanduser('~/tencent_comic')
        self.pathLine.setText(defaultPath)
        
        self.browseButtun = QPushButton("浏览")
        self.browseButtun.clicked.connect(self.getPath)

        comicNameLabel = QLabel("漫画名: ")
        self.comicName = QLabel("暂无")
        
        comicIntroLabel = QLabel("简介: ")
        self.comicIntro = QLabel("暂无")
        self.comicIntro.setWordWrap(True)

        chapterGroupBox = QGroupBox("章节列表:")
        
        self.chapterListView = QListWidget(chapterGroupBox)
        self.chapterListView.setSelectionMode(QAbstractItemView.ExtendedSelection)

        groupBoxLayout = QHBoxLayout(chapterGroupBox)
        groupBoxLayout.addWidget(self.chapterListView)

        mainLayout = QGridLayout()
        mainLayout.addWidget(nameLabel, 0, 0)
        mainLayout.addWidget(self.nameLine, 0, 1)
        mainLayout.addWidget(self.analysisButton, 0, 2)
        mainLayout.addWidget(pathLineLabel, 1, 0)
        mainLayout.addWidget(self.pathLine, 1, 1)
        mainLayout.addWidget(self.browseButtun, 1, 2)
        mainLayout.addWidget(comicNameLabel, 2, 0)
        mainLayout.addWidget(self.comicName, 2, 1, 1, 2)
        mainLayout.addWidget(comicIntroLabel, 3, 0)
        mainLayout.addWidget(self.comicIntro, 3, 1, 1, 2)
        mainLayout.addWidget(chapterGroupBox, 4, 0, 1, 3)

        self.setLayout(mainLayout)
        self.setWindowTitle("腾讯漫画下载")
        self.setGeometry(400, 300, 800, 500)

    def getPath(self):
        path = str(QFileDialog.getExistingDirectory(self, "选择下载目录"))
        if path:
            self.pathLine.setText(path)

    def anaysisURL(self):
        url = self.nameLine.text()

        if getComic.isLegelUrl(url):
            id = getComic.getId(url)
            comicName,comicIntrd,count,contentList = getComic.getContent(id)

            contentNameList = []
            for item in contentList:
                for k in item:
                    contentNameList.append(item[k]['t'])
            
            self.comicName.setText(comicName)
            self.comicIntro.setText(comicIntrd)
            self.chapterListView.clear()
            self.chapterListView.addItems(contentNameList)

        else:
            QMessageBox.about(self, "错误", "错误的URL!")

if __name__ == '__main__':
    import sys

    app = QApplication(sys.argv)

    main = TencentComicDownloader()
    main.show()

    app.exec_()
