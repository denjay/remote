import json
import os
import pickle
import socket
import subprocess
import sys
from functools import wraps

from flask import jsonify, request


def ip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]


class Config(object):
    def __init__(self):
        self.version = 1.0
        self.ip = ip()
        """如果有配置文件，就从配置文件获取配置，否则创建配置文件"""
        if os.path.exists(sys.path[0] + '/config.pkl'):
            with open(sys.path[0] + '/config.pkl', 'rb') as config:
                dic = pickle.load(config)
            self.match_code = dic.get('match_code')
            self.front_end_config = dic.get('front_end_config')
            self.close_screen = dic.get('close_screen')
            self.skin = dic.get('skin')
            self.mode = dic.get('mode')
            self.x = dic.get('x')
            self.y = dic.get('y')
        else:
            self.match_code = "1234"  # 匹配码
            self.front_end_config = 0b0010  # 前端设置
            self.close_screen = 0  # 0表示执行命令后不自动息屏
            self.skin = 0
            self.mode = 1  # 0表示mini mode,1表示normal mode
            self.x = 0  # 窗口x坐标
            self.y = 0  # 窗口y坐标
            # 启动器图标所需内容,下面StartupWMClass作用是让任务栏只有一个图标，即使在任务栏创建了图标
            content = """[Desktop Entry]
Encoding=UTF-8
Name=remote
StartupWMClass=Tk
Comment=远程控制电脑关机
Exec=python3 {}
Icon = {}
Categories=Application;
Version={}
Type=Application
Terminal=false
""".format(sys.path[0] + '/remote.py', sys.path[0] + '/assets/ICON.png', self.version)
            path = os.environ['HOME'] + \
                '/.local/share/applications/Remote.desktop'
            with open(path, 'w+') as f:
                f.write(content)

    def save_config(self):
        """保存配置到配置文件"""
        dic = {
            'front_end_config': self.front_end_config if self.front_end_config else 0,
            'match_code': self.match_code,
            'close_screen': self.close_screen,
            'skin': self.skin,
            'mode': self.mode,
            'x': self.x,
            'y': self.y,
        }
        with open(sys.path[0] + '/config.pkl', 'wb') as config:
            pickle.dump(dic, config)


config = Config()


def validate_match_code(func):
    @wraps(func)
    def wrapper(*args, **kw):
        if request.method == "POST":
            data = json.loads(request.data)
        elif request.method == "GET":
            data = request.args
        if data["match_code"] != config.match_code:
            return jsonify({"message": "匹配码不正确"})
        else:
            return func(*args, **kw)
    return wrapper


def close_screen(func):
    @wraps(func)
    def wrapper(*args, **kw):
        result = func(*args, **kw)
        if config.front_end_config & 0b0100 == 0b0100:
            subprocess.call("xset dpms force off &", shell=True)
        return result
    return wrapper
