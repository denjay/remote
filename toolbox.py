import json
import os
import pickle
import socket
import sys
import subprocess
from functools import wraps

from flask import request, jsonify


def validate_hostname(func):
    @wraps(func)
    def wrapper(*args, **kw):
        if request.method == "POST":
            data = json.loads(request.data)
        elif request.method == "GET":
            data = request.args
        if data["hostname"] != config.hostname:
            return jsonify({"message": "匹配码不正确"})
        else:
            return func(*args, **kw)
    return wrapper


def close_screen(func):
    @wraps(func)
    def wrapper(*args, **kw):
        result = func(*args, **kw)
        subprocess.call("xset dpms force off &", shell=True)
        return result
    return wrapper


def ip():
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.connect(('8.8.8.8', 80))
        return s.getsockname()[0]


def hostname():
    if os.path.exists(sys.path[0] + '/config.pkl'):
        with open(sys.path[0] + '/config.pkl', 'rb') as config:
            dic = pickle.load(config)
            return dic.get('hostname')
    else:
        return socket.gethostname()


class Config(object):
    def __init__(self):
        self.version = 1.0
        self.ip = ip()
        """如果有配置文件，就从配置文件获取配置，否则创建配置文件"""
        if os.path.exists(sys.path[0] + '/config.pkl'):
            with open(sys.path[0] + '/config.pkl', 'rb') as config:
                dic = pickle.load(config)
            self.hostname = dic.get('hostname')
            self.auto_starts = dic.get('auto_starts')
            self.close_screen = dic.get('close_screen')
            self.skin = dic.get('skin')
            self.mode = dic.get('mode')
            self.x = dic.get('x')
            self.y = dic.get('y')
        else:
            self.hostname = hostname()
            self.auto_starts = 0  # 0表示不自启
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

            # 创建run.sh脚本
            command = """#!/bin/sh
if [ -e {0} ]; then
    sleep 1m
    python3 "{0}" 1
fi
            """.format(sys.path[0] + '/remote.py')
            with open(sys.path[0] + '/run.sh', 'w+') as f:
                f.write(command)

    def save_config(self):
        """保存配置到配置文件"""
        dic = {
            'auto_starts': self.auto_starts,
            'hostname': self.hostname,
            'close_screen': self.close_screen,
            'skin': self.skin,
            'mode': self.mode,
            'x': self.x,
            'y': self.y,
        }
        with open(sys.path[0] + '/config.pkl', 'wb') as config:
            pickle.dump(dic, config)


config = Config()
