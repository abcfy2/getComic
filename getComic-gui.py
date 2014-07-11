#!/usr/bin/env python3

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *


class TencentComicDownloader(QWidget):
    def __init__(self, parent=None):
        super(TencentComicDownloader, self).__init__(parent)

        nameLabel = QLabel("漫画首页:")
        self.nameLine = QLineEdit()

        self.analysisButton = QPushButton("分析")

        pathLineLabel = QLabel("下载路径:")
        self.pathLine = QLineEdit()
        
        self.browseButtun = QPushButton("浏览")

        comicNameLabel = QLabel("漫画名: ")
        self.comicName = QLabel("暂无（占位用）")
        
        comicIntroLabel = QLabel("简介: ")
        self.comicIntro = QLabel("暂无（占位用）")

        chapterListLabel = QGroupBox("章节列表:")

        mainLayout = QGridLayout()
        mainLayout.addWidget(nameLabel, 0, 0)
        mainLayout.addWidget(self.nameLine, 0, 1)
        mainLayout.addWidget(self.analysisButton, 0, 2)
        mainLayout.addWidget(pathLineLabel, 1, 0, Qt.AlignTop)
        mainLayout.addWidget(self.pathLine, 1, 1)
        mainLayout.addWidget(self.browseButtun, 1, 2)
        mainLayout.addWidget(comicNameLabel, 2, 0)
        mainLayout.addWidget(self.comicName, 2, 1)
        mainLayout.addWidget(comicIntroLabel, 3, 0)
        mainLayout.addWidget(self.comicIntro, 3, 1)
        mainLayout.addWidget(chapterListLabel, 4, 0)

        self.setLayout(mainLayout)
        self.setWindowTitle("腾讯漫画下载")
        self.setGeometry(0, 0, 800, 0)

if __name__ == '__main__':
    import sys

    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    main = TencentComicDownloader()
    main.show()

    sys.exit(app.exec_())
