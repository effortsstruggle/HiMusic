import sys
from PIL import ImageQt, ImageFilter
from PyQt5.QtWidgets import (QMessageBox, QApplication)
from PyQt5.QtCore import QSharedMemory
from widgets import MainWindow, CommonHelper, GlobalVar


# 寻找目录下歌词文件和图片文件
def is_memory_attach(key):
    GlobalVar.share = QSharedMemory()
    GlobalVar.share.setKey(key)

    if GlobalVar.share.attach():
        QMessageBox.warning(None, '程序已在运行', '程序已在运行，请关闭后重试。')
        return True
    else:
        GlobalVar.share.create(1)
        return False

def main():
    GlobalVar.app = QApplication(sys.argv)
    GlobalVar.helper = CommonHelper.CommonHelper()

    if is_memory_attach('HiMusic'):
        return
    GlobalVar.window = MainWindow.MainWindow()

    # 显示窗体并运行
    GlobalVar.window.show()
    sys.exit(GlobalVar.app.exec_())

if __name__ == '__main__':
    main()