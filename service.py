import os
import subprocess
from pykeyboard import PyKeyboard

from flask import Flask, request
from flask_cors import CORS

from toolbox import host_info, validate_hostname


def run_flask(label):
    app = Flask(__name__)
    CORS(app)

    @app.route("/")
    @validate_hostname
    def index():
        '''返回首页'''
        return host_info["ip"] + host_info["hostname"]

    @app.route("/exec")
    @validate_hostname
    def exec():
        '''直接执行收到的代码'''
        code = request.args["code"]
        print(code)
        result = os.system(code)
        # result = subprocess.run(code)
        print("result:", result)
        return str(result)

    @app.route("/order")
    @validate_hostname
    def order():
        '''收到的是语义化的命令'''
        code = request.args["code"]
        pass

    label.config(text='成功启动服务')
    try:
        app.run(port=8765, host="0.0.0.0")
    except OSError as e:
        label.config(text='端口被占用')
