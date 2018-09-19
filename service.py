import json
import subprocess
from pykeyboard import PyKeyboard

from flask import Flask, request, render_template
from flask_cors import CORS

from toolbox import host_info, validate_hostname


def run_flask(label):
    app = Flask(__name__)
    CORS(app)

    @app.route("/")
    def index():
        '''返回首页'''
        return render_template("remote_ui.html", hostname=host_info["hostname"])

    @app.route("/exec", methods=["post"])
    @validate_hostname
    def exec():
        '''直接执行收到的代码'''
        data = json.loads(request.get_data())
        description = data["description"]
        code = data["code"]
        result = subprocess.call(code + " &", shell=True)
        label.config(text=description)
        return str(result)

    @app.route("/order", methods=["post"])
    @validate_hostname
    def order():
        '''收到的是语义化的命令'''
        k = PyKeyboard()
        key_map = {
            "播放/暂停": [k.control_key, k.alt_key, "p"],
            "上一曲": [k.control_key, k.alt_key, k.left_key],
            "下一曲": [k.control_key, k.alt_key, k.right_key],
            "音量加": [k.control_key, k.alt_key, k.up_key],
            "音量减": [k.control_key, k.alt_key, k.down_key],
        }
        data = json.loads(request.get_data())
        description = data["description"]
        if description in key_map:
            k.press_keys(key_map[description])
            label.config(text=description)
            return "0"
        else:
            return "找不到相应的快捷键"

    label.config(text='成功启动服务')
    try:
        app.run(port=8765, host="0.0.0.0")
    except OSError as e:
        label.config(text='端口被占用')
