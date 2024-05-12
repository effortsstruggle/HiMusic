import json
from app import mapi

# 帮助
class CommonHelper:
    engine = mapi.EngineKuwo
    default_engine = mapi.EngineKuwo
    engines = {}
    settings = {}
    cache = {}
    qss = []

    def __init__(self):
        # 读取 QSS 文件
        self.read_qss('qss/style.qss')
        self.read_qss('qss/buttons.qss')
        # 读取设置
        self.read_settings()
        # 读取缓存
        self.read_cache()
        # 设置引擎
        self.set_engine()

        print(f"qss: {self.qss}")
        print(f"setting: {self.settings}")
        print(f"cache: {self.cache}")


    # 读取QSS文件
    def read_qss(self, style):
        with open(style, 'r', encoding='utf-8') as f:
            self.qss.append(f.read())

    # 读取设置
    def read_settings(self):
        try:
            settings = json.load(open('datas/settings.json', 'r'))
        except:
            with open('datas/settings.json', 'w') as f:
                f.write('{}')
            settings = {}
        #字典函数 setdefault() , 若键不存在于字典中,将会添加键并将值设为default
        settings.setdefault('general', {})
        settings.setdefault('lrcs', {})
        settings.setdefault('download', {})
        self.settings = settings

    # 读取缓存
    def read_cache(self):
        try:
            cache = json.load(open('datas/cache.json', 'r'))
        except:
            with open('datas/cache.json', 'w') as f:
                f.write('{}')
            cache = {}
        cache.setdefault('last_song', [])
        cache.setdefault('last_playlist', [])
        cache.setdefault('collections', [])
        self.cache = cache

    # 设置搜索引擎
    def set_engine(self):
        self.engines = {}
        for s in dir(mapi):
            if s.startswith('Engine'):
                engine = eval(f'mapi.{s}')
                self.engines[engine.pre] = engine
                if engine.pre == self.settings['general'].setdefault('default_engine', 'kuwo'):
                    self.engine = engine
                    self.default_engine = engine

    # 保存设置
    def save_settings(self):
        json.dump(self.settings, open('datas/settings.json', 'w'), indent=4)

    # 保存缓存
    def save_cache(self):
        json.dump(self.cache, open('datas/cache.json', 'w'), indent=4)