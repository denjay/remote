import json
import os
import subprocess
from pykeyboard import PyKeyboard

from flask import Flask, request, render_template, send_from_directory, send_file, redirect, url_for, jsonify
from flask_cors import CORS

from toolbox import host_info, validate_hostname


def run_flask(label, root):
    app = Flask(__name__)
    CORS(app)

    @app.route("/")
    def index():
        '''返回首页'''
        return render_template("index.html")

    @app.route('/get_clipboard_content', methods=["post", "get"])
    @validate_hostname
    def get_clipboard_content():
        text = root.clipboard_get()
        # root.clipboard_clear()  # 清除剪贴板内容
        # root.clipboard_append("xxooxx")  # 向剪贴板追加内容
        if request.method == "POST":
            if os.path.isfile(text):
                return jsonify({"file_url": url_for("get_clipboard_content", hostname=host_info["hostname"])})
            else:
                label.config(text="获取剪贴板文字")
                return jsonify({"text": text})
        elif request.method == "GET":
            label.config(text="获取剪贴板文件")
            filename = os.path.basename(text)
            return send_file(text, mimetype='application/octet-stream', as_attachment=True, attachment_filename=filename)

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'assets'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

    @app.route("/exec", methods=["post"])
    @validate_hostname
    def exec():
        '''直接执行收到的代码'''
        data = json.loads(request.get_data())
        description = data["description"]
        code = data["code"]
        result = subprocess.call(code + " &", shell=True)
        label.config(text=description)
        return jsonify({"message": result})

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
        data = json.loads(request.data)
        description = data["description"]
        if description in key_map:
            k.press_keys(key_map[description])
            label.config(text=description)
            return jsonify({"message": 0})
        else:
            return jsonify({"message": "找不到相应的快捷键"})

    label.config(text='成功启动服务')
    try:
        app.run(port=8765, host="0.0.0.0")
    except OSError as e:
        label.config(text='端口被占用')
