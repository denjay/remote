import json
import os
import pickle
import socket
import sys
import subprocess
from functools import wraps

from flask import request, jsonify


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


host_info = {"hostname": hostname(), "ip": ip()}


def validate_hostname(func):
    @wraps(func)
    def wrapper(*args, **kw):
        if request.method == "POST":
            data = json.loads(request.data)
        elif request.method == "GET":
            data = request.args
        if data["hostname"] != host_info["hostname"]:
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
