import os
import socket

from flask import Flask, request
from flask_cors import CORS


def run_flask(label, hostname):
    app = Flask(__name__)
    CORS(app)

    @app.route("/exec")
    def exec():
        order = request.args["order"]
        if hostname != request.args["host_name"]:
            return "匹配不成功，请核对"
        result = os.popen(order)
        return result

    @app.route("/")
    def index():
        ip = ""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        finally:
            s.close()
        return ip

    label.config(text='成功启动服务')
    try:
        app.run(port=8765, host="0.0.0.0")
    except OSError as e:
        label.config(text='端口被占用')
