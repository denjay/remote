import json
import os
import pickle
import socket
import sys
from functools import wraps

from flask import request


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
        data = json.loads(request.get_data())
        if data["hostname"] != host_info["hostname"]:
            return "匹配码不正确"
        else:
            return func(*args, **kw)
    return wrapper
