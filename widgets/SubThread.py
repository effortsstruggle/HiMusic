from PyQt5.QtCore import (Qt, QThread, pyqtSignal)
from PyQt5.QtGui import (QImage, QPixmap)
from re import fullmatch, I
from os import walk
from app import mapi
from widgets import GlobalVar

# 分离sign
def split_sign(sign):
    engine, *datas = sign.split(':')
    data = ':'.join(datas)
    return engine, data

def find_lrc_img_in_path(url, mode='lrcimg'):
    img_file = ''
    lrc_file = ''
    # 匹配后缀
    allowed_imgs = ['jpg', 'png']
    allowed_lrcs = ['lrc']
    # 遍历
    *paths, name = url.split('/')
    path = '/'.join(paths)
    file_name = '.'.join(name.split('.')[:-1])
    all_files = walk(path)
    # 结果
    lrc_file = ''
    img_file = ''
    # 目标路径正则
    lrc_path_regex = f'{path}(/((lrc)|(lrcs)))?'
    img_path_regex = f'{path}(/((image)|(img)|(images)|(imgs)))?'

    # 遍历
    for path, dir, filelist in all_files:
        # 格式化
        path = path.replace('\\', '/')

        # 路径是否合法
        is_lrc_path_valid = bool(fullmatch(lrc_path_regex, path, I))
        is_img_path_valid = bool(fullmatch(img_path_regex, path, I))
        if not (is_lrc_path_valid or is_img_path_valid):
            continue

        # 遍历文件
        for file in filelist:
            # 文件名和后缀
            name = '.'.join(file.split('.')[:-1])
            suffix = file.split('.')[-1]

            # 文件名不匹配
            if name != file_name:
                continue
            # 文件未有 且 后缀匹配 且 路径匹配
            if (not lrc_file) and (suffix in allowed_lrcs) and is_lrc_path_valid:
                lrc_file = path + '/' + file
                break
            if (not img_file) and (suffix in allowed_imgs) and is_img_path_valid:
                img_file = path + '/' + file
                break

        # 如果两个文件都有就退出
        if all([lrc_file, img_file]):
            break

    return img_file, lrc_file
class SubThread(QThread):
    """
        线程类
    """
    finished = pyqtSignal(list)
    result_finished = pyqtSignal(list)
    pixmap_finished = pyqtSignal(QPixmap)
    img_finished = pyqtSignal(QPixmap)
    lrcs_finished = pyqtSignal(list)
    music_url_finished = pyqtSignal(str)
    music_content_finished = pyqtSignal(bytes)

    arg = [] # 参数
    args = {} # 参数
    task = None # 任务

    def __init__(self, task, finished=None, *arg, **args):
        QThread.__init__(self)

        self.arg = arg      #参数
        self.args = args    #参数
        self.task = task    #任务

        if finished != None:
            self.finished.connect(finished)

    # 入口
    def run(self):
        result = self.task(self, *self.arg, **self.args)

    # 获取搜索结果
    def get_result(self, keyword):
        try:
            datas = GlobalVar.helper.engine.search(keyword)
        except:
            datas = []

        self.result_finished.emit(datas)

    # 获取小图片
    def get_pixmap(self, data):
        engine, url = split_sign(data)

        if not url:
            return

        try:
            img = GlobalVar.helper.engines[engine].get_pic(url)

            # 图片
            img = QImage.fromData(img)
            img = QPixmap.fromImage(img)
            pixmap = img.scaled(40, 40, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        except:
            return

        self.pixmap_finished.emit(pixmap)

    # 获取大图片
    def get_img(self, data):
        if not data:
            return

        engine, url = split_sign(data)

        try:
            content = GlobalVar.helper.engines[engine].get_pic(url)

            # 图片
            img = QImage.fromData(content)
            pixmap = QPixmap.fromImage(img).scaled(240, 240, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        except:
            return

        self.img_finished.emit(pixmap)

    def get_local_pixmap(self, url):
        img_url = find_lrc_img_in_path(url, 'img')[0]
        pixmap = QPixmap(img_url)
        try:
            pixmap = pixmap.scaled(40, 40, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        except:
            pass

        self.pixmap_finished.emit(pixmap)

    def get_local_img(self, url):
        img_url = find_lrc_img_in_path(url, 'img')[0]
        pixmap = QPixmap(img_url)
        try:
            img = pixmap.scaled(240, 240, Qt.IgnoreAspectRatio, Qt.SmoothTransformation)
        except:
            pass

        self.img_finished.emit(img)

    # 获取歌词
    def get_lrcs(self, data):
        engine, sign = split_sign(data)

        try:
            lrcs = GlobalVar.helper.engines[engine].get_music_lrc(sign)
        except:
            return

        self.lrcs_finished.emit(lrcs)

    def get_local_lrcs(self, url):
        lrc_url = find_lrc_img_in_path(url, 'lrc')[1]

        with open(lrc_url, 'r') as f:
            lrcs_str = f.read()

        lrcs = mapi.format_lrc(lrcs_str)

        self.lrcs_finished.emit(lrcs)

    # 获取音乐 URL
    def get_music_url(self, data):
        music_url = ''
        engine, url = split_sign(data)
        try:
            music_url = GlobalVar.helper.engines[engine].get_music_url(url)
        except Exception as e:
            music_url = 'error:' + str(e)

        self.music_url_finished.emit(music_url)

    def get_music_content(self, data):
        engine, url = split_sign(data)
        try:
            content = GlobalVar.helper.engines[engine].get_music_content(url)
        except:
            return

        self.music_content_finished.emit(content)