import json
import os
import subprocess
import time

from flask import (Flask, jsonify, render_template, request, send_file,
                   send_from_directory, url_for)
from flask_cors import CORS
from pykeyboard import PyKeyboard

from toolbox import close_screen, config, validate_match_code


def run_flask(label, root):
    app = Flask(__name__)
    CORS(app)

    @app.route("/")
    def index():
        '''返回首页'''
        return render_template("index.html")

    @app.route('/get_clipboard_content', methods=["post", "get"])
    @validate_match_code
    def get_clipboard_content():
        try:
            text = root.clipboard_get()
        except:
            return jsonify({"message": "剪贴板无内容"})
        # root.clipboard_clear()  # 清除剪贴板内容
        if request.method == "POST":
            if os.path.isfile(text):
                return jsonify({"file_url": url_for("get_clipboard_content", hostname=config.hostname)})
            else:
                label.config(text="获取剪贴板文字")
                return jsonify({"text": text})
        elif request.method == "GET":
            label.config(text="获取剪贴板文件")
            filename = os.path.basename(text)
            return send_file(text, mimetype='application/octet-stream', as_attachment=True, attachment_filename=filename)

    @app.route('/set_clipboard_content', methods=["post"])
    @validate_match_code
    def set_clipboard_content():
        content = json.loads(request.data)["content"]
        root.clipboard_append(content)
        label.config(text="剪贴板收到文字")
        return jsonify({"message": "已经将文字传到电脑剪贴板"})

    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'assets'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')

    @app.route("/exec", methods=["post"])
    @validate_match_code
    def exec():
        '''直接执行收到的代码'''
        data = json.loads(request.get_data())
        description = data["description"]
        code = data["code"]
        result = subprocess.call(code + " &", shell=True)
        label.config(text=description)
        return jsonify({"message": result})

    @app.route("/hot_key", methods=["post"])
    @validate_match_code
    @close_screen
    def hot_key():
        '''快捷键命令'''
        k = PyKeyboard()
        key_map = {
            "播放/暂停": [k.control_key, k.alt_key, "p"],
            "上一曲": [k.control_key, k.alt_key, k.left_key],
            "下一曲": [k.control_key, k.alt_key, k.right_key],
            "音量加": [k.control_key, k.alt_key, k.up_key],
            "音量减": [k.control_key, k.alt_key, k.down_key],
            "待机": ([k.control_key, k.alt_key, k.delete_key], k.left_key, k.enter_key),
        }
        data = json.loads(request.data)
        description = data["description"]
        if description not in key_map:
            return jsonify({"message": "找不到相应的快捷键"})
        # 判断是否打开了网易云音乐
        if description in ["播放/暂停", "上一曲", "下一曲", "音量加", "音量减"] and subprocess.run("pgrep netease-cloud-m", shell=True).returncode == 1:
            subprocess.call("netease-cloud-music &", shell=True)
            time.sleep(2)
        keys_comb = key_map[description]
        if isinstance(keys_comb, tuple):
            for item in keys_comb:
                time.sleep(0.1)
                if isinstance(item, list):
                    k.press_keys(item)
                else:
                    k.tap_key(item)
        elif isinstance(keys_comb, list):
            k.press_keys(keys_comb)
        else:
            k.tap_key(keys_comb)
        label.config(text=description)
        return jsonify({"message": 0})

    @app.route("/configuration", methods=["post"])
    @validate_match_code
    def configuration():
        if "front_end_config" in json.loads(request.data):
            config.front_end_config = json.loads(
                request.data)["front_end_config"]
            config.save_config()
            return jsonify({"message": 0})
        else:
            return jsonify({"front_end_config": config.front_end_config})

    label.config(text='成功启动服务')
    try:
        app.run(port=8765, host="0.0.0.0")
    except OSError as e:
        label.config(text='端口被占用')
