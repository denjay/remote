#!/usr/bin/python3

"""
由于hosts文件经常失效，手动改hosts还是挺麻烦的，所以写了这个软件。
这是我学Python没多久时写的，所以代码质量可能一般般。
软件安装方法：
1、首先获得hosts文件的读写权限，最简单的方法是执行命令：sudo chmod 777 /etc/hosts
   如果觉得这种方法不安全，可以将本py文件所有者改为root，然后给本文件加上setuid标志。
2、安装python3的tkinter模块，命令： sudo apt-get install python3-tk
3、打开终端，在终端中输入命令：python3  路径/Hosts助手.py
4、成功，以后可以从启动器打开
"""

import os
import pickle
import re
import sys
import threading
import tkinter as tk

import qrcode

import setproctitle
from service import run_flask
from toolbox import host_info


class Remote(object):
    def __init__(self):
        """给软件设置初始参数"""
        self.version = 1.0
        self.x = 0  # 窗口x坐标
        self.y = 0  # 窗口y坐标
        self.x_relative = 0  # 相对坐标x
        self.y_relative = 0  # 相对坐标y
        self.auto = 0  # 0表示不自启
        self.service_status = 0  # 0表示没有运行服务器
        self.skins = [('#1F2326', 'black', '#1F2336', '#00ffff', '#1F2326',  '#00ffff'),
                      ('#FFFFFF', '#90ee90', '#D0D0D0', '#00ced1', '#00ced1', '#FFFFFF')
                      ]
        self.skin = 0
        self.mode = 1  # 0表示mini mode,1表示normal mode
        self.button_list = []  # 按钮列表
        self.entry = None  # 文本框对象
        self.entry_content = ""
        self.root = None
        self.frame = None
        self.label = None
        self.img_label = None
        self.close_button_label = None
        self.img_close = None
        self.img_close_hover = None

    def run_service(self):
        """更新hosts操作的主进程"""
        thr = threading.Thread(target=run_flask, args=(self.label,))
        thr.daemon = True
        thr.start()

    def get_config(self):
        """如果有配置文件，就从配置文件获取配置，否则创建配置文件"""
        if os.path.exists(sys.path[0] + '/config.pkl'):
            with open(sys.path[0] + '/config.pkl', 'rb') as config:
                dic = pickle.load(config)
            self.auto = dic.get('auto')
            self.skin = dic.get('skin')
            self.mode = dic.get('mode')
            self.x = dic.get('x')
            self.y = dic.get('y')
        else:
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
""".format(os.path.realpath(__file__), sys.path[0] + '/assets/ICON.png', self.version)
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
            """.format(os.path.realpath(__file__))
            with open(sys.path[0] + '/run.sh', 'w+') as f:
                f.write(command)

    def save_config(self):
        """保存配置到配置文件"""
        self.x = self.root.winfo_x()
        self.y = self.root.winfo_y()
        dic = {'auto': self.auto, 'hostname': host_info["hostname"], 'skin': self.skin, 'mode': self.mode, 'x': self.x, 'y': self.y}
        with open(sys.path[0] + '/config.pkl', 'wb') as config:
            pickle.dump(dic, config)

    def generate_qrcode(self):
        qr = qrcode.QRCode(box_size=5, border=0)
        qr.add_data("http://{}:8765/".format(host_info["ip"]))
        img = qr.make_image(fill_color=self.skins[self.skin][4], back_color=self.skins[self.skin][5])
        img.save('qrcode.png')
        self.qrcode = tk.PhotoImage(file="qrcode.png")
        self.img_label["image"] = self.qrcode

    def validate(self, *args):
        '''动态生成二维码'''
        # 验证输入框数据
        data = self.entry_content.get()
        if not re.match(r"^[0-9a-zA-Z\_\-]{0,10}$", data):
            self.label.config(text='输入不合法')
            self.entry_content.set(host_info["hostname"])
        else:
            host_info["hostname"] = data
            self.label.config(text='已更新匹配码')

    def mini_mode(self, e):
        """切换界面显示模式"""
        self.mode = 0 if self.img_label.winfo_ismapped() else 1
        if self.mode:
            for child in self.root.children.values():
                if child != self.label:
                    child.grid()
            self.root.geometry('+{}+{}'.format(self.x, self.y))
        else:
            for child in self.root.children.values():
                if child != self.label:
                    child.grid_remove()
            self.root.geometry('+{}+{}'.format(self.x, self.y + 20))

    def dialog(self):
        """显示软件说明"""

        def close_dialog(e):
            dialog.destroy()

        dialog = tk.Toplevel(self.root)
        dialog.overrideredirect(True)
        dialog.geometry(
            '+{}+{}'.format(self.root.winfo_screenwidth() // 2 - 180, self.root.winfo_screenheight() // 2 - 135))
        dialog["background"] = self.skins[self.skin][0]
        dialog.resizable(False, False)
        dialog.wm_attributes('-topmost', 1)
        content = """    软件：Hosts助手    软件版本：{}     作者：杰哥
    说明：hosts文件源来自互联网，本人不保证安全，可自行修改。
    如果修改后发现有问题，可以点击还原hosts按钮，还原到最初。
    替换hosts文件后可能不会立即生效，可以关闭/开启网络，或
    启用/禁用飞行模式让域名解析立即生效。
    开机自启表示软件会在开机时在后台启动并自动更新hosts，直
    到成功。软件选择地址列表中连接最快的作为源文件，各源内容
    不相同。更新hosts完成后，地址显示红色的表示超时或者失效，
    显示绿色的表示最终的hosts文件来源。"""
        sub_label = tk.Label(dialog, text=content.format(self.version),
                             justify=tk.LEFT, anchor=tk.W, fg=self.skins[self.skin][3], relief=tk.FLAT,
                             highlightthickness=0.4, bg=self.skins[self.skin][0], width=51, height=10)
        sub_label.bind('<Button-1>', close_dialog)
        sub_label.pack()

    def auto_starts(self):
        """设置是否开机后台启动"""
        PATH = os.environ['HOME'] + '/.profile'
        content = """
# For Hosts assistant
if [ -e "{0}" ]; then
    . {0} &
fi"""
        script = content.format(sys.path[0] + '/run.sh')
        if self.auto == 0:
            self.auto = 1
            with open(PATH, 'a') as f:
                f.write(script)
        else:
            self.auto = 0
            with open(PATH, 'r+') as f:
                result = f.read().replace(script, '')
                f.truncate(0)
                f.seek(0, 0)
                f.write(result)
        self.button_list[1]['text'] = ('开机自启', '取消自启')[self.auto]

    def change_skin(self):
        """切换皮肤"""
        self.skin = (self.skin + 1) % len(self.skins)
        self.generate_qrcode()
        self.root["bg"] = self.skins[self.skin][0]
        self.label["fg"] = self.skins[self.skin][3]
        self.label["bg"] = self.skins[self.skin][2]
        self.entry["fg"] = self.skins[self.skin][3]
        self.entry["bg"] = self.skins[self.skin][0]
        self.img_label["fg"] = self.skins[self.skin][3]
        self.img_label["bg"] = self.skins[self.skin][0]
        self.close_button_label["fg"] = self.skins[self.skin][3]
        self.close_button_label["bg"] = self.skins[self.skin][0]
        for bt in self.button_list:
            bt["fg"] = self.skins[self.skin][3]
            bt["bg"] = self.skins[self.skin][0]
            bt["activebackground"] = self.skins[self.skin][2]
            bt["activeforeground"] = self.skins[self.skin][3]
            bt["highlightbackground"] = self.skins[self.skin][1]

    def quit(self, e):
        self.save_config()
        sys.exit()

    def change_close_button_img(self, e):
        '''标题栏关闭按钮变化'''
        if e.type._name_ == "Enter":
            self.close_button_label["image"] = self.img_close_hover
        elif e.type._name_ == "Leave":
            self.close_button_label["image"] = self.img_close

    def move(self, e):
        '''移动窗口'''
        if e.x_root < self.root.winfo_screenwidth() - 10:
            new_x = e.x - self.x_relative + self.root.winfo_x()
            new_y = e.y - self.y_relative + self.root.winfo_y()
            if new_x < 10:
                new_x = 0
            if new_x > self.root.winfo_screenwidth() - self.root.winfo_width() - 10:
                new_x = self.root.winfo_screenwidth() - self.root.winfo_width()
            # 自动隐藏
            # if new_x > self.root.winfo_screenwidth() - self.root.winfo_width() - 10:
            #     new_x = self.root.winfo_screenwidth() - 4
            if new_y < 10:
                new_y = 0
            if new_y > self.root.winfo_screenheight() - self.root.winfo_height() - 10:
                new_y = self.root.winfo_screenheight() - self.root.winfo_height()
            self.x = new_x
            self.y = new_y
            self.root.geometry('+{}+{}'.format(self.x, self.y))

    def click(self, e):
        '''左键单击窗口时获得鼠标位置，辅助移动窗口'''
        self.x_relative = e.x
        self.y_relative = e.y

    def select_text(self, e):
        self.entry.select_range(0, tk.END)

    def run_gui(self):
        """启动软件主界面"""
        self.root = tk.Tk()
        self.root.title('')
        img = tk.PhotoImage(file=sys.path[0] + '/assets/ICON.png')
        self.root.tk.call('wm', 'iconphoto', self.root._w, img)
        # 主窗口
        if self.x == self.y == 0:
            self.x = self.root.winfo_screenwidth() // 2 - 100
            self.y = self.root.winfo_screenheight() // 2 - 200
        self.root.geometry('+{}+{}'.format(self.x, self.y))
        self.root["background"] = self.skins[self.skin][0]
        self.root.resizable(False, False)  # 固定窗口大小
        self.root.wm_attributes('-topmost', 1)  # 置顶窗口
        self.root.wm_attributes('-type', 'splash')
        self.root.bind('<Button-1>', self.click)
        self.root.bind('<B1-Motion>', self.move)
        # 标题栏及关闭按钮
        self.img_close = tk.PhotoImage(file="./assets/titlebutton-close.png")
        self.img_close_hover = tk.PhotoImage(file="./assets/titlebutton-close-hover.png")
        self.close_button_label = tk.Label(self.root, image=self.img_close, width=20, height=20, fg=self.skins[self.skin][3], bg=self.skins[self.skin][0])
        self.close_button_label.grid(column=1, ipadx=2, sticky=tk.E)
        self.close_button_label.bind('<ButtonPress-1>', self.quit)  # 添加单击事件
        self.close_button_label.bind('<Enter>', self.change_close_button_img)
        self.close_button_label.bind('<Leave>', self.change_close_button_img)
        # 消息框
        self.label = tk.Label(self.root, text='消息框', bg=self.skins[self.skin][2], fg=self.skins[self.skin][3], font=("Arial, 12"), relief=tk.FLAT, width=19)
        self.label.grid(ipady=2, column=0, columnspan=2, row=1)
        self.label.bind('<Double-Button-1>', self.mini_mode)  # 添加双击事件
        self.label.bind('<Button-3>', self.quit)
        # 按钮组
        button_configs = [
            (('开机自启', '取消自启')[self.auto], self.auto_starts, 1, 2),
            ('切换主题', self.change_skin, 0, 3),
            ('软件说明', self.dialog, 1, 3),
            ]
        for bc in button_configs:
            button = tk.Button(self.root, text=bc[0], relief=tk.FLAT, command=bc[1], highlightthickness=0.5, fg=self.skins[self.skin][3], bg=self.skins[self.skin][0], activebackground=self.skins[self.skin][2], activeforeground=self.skins[self.skin][3], highlightbackground=self.skins[self.skin][1])
            button.grid(column=bc[2], row=bc[3], padx=3,
                        pady=3, sticky=tk.N + tk.E + tk.S + tk.W)
            self.button_list.append(button)
        # 输入框
        self.entry_content = tk.StringVar()
        self.entry = tk.Entry(self.root, fg=self.skins[self.skin][3], bg=self.skins[self.skin][0], width=10, textvariable=self.entry_content, justify=tk.CENTER, highlightthickness=0.5, highlightbackground='#4F4F4F', highlightcolor='#4F4F4F', insertbackground=self.skins[self.skin][3], relief=tk.FLAT)
        self.entry_content.set(host_info["hostname"])
        self.entry_content.trace_add("write", self.validate)
        self.entry.grid(column=0, row=2, padx=3, pady=3, sticky=tk.N + tk.E + tk.S + tk.W)
        self.entry.bind('<ButtonPress-1>', self.select_text)  # 添加单击事件

        # 二维码界面
        self.img_label = tk.Label(self.root, width=150, height=150, fg=self.skins[self.skin][3], bg=self.skins[self.skin][0])
        self.generate_qrcode()
        self.img_label.grid(column=0, columnspan=2, row=6)
        # 迷你模式时隐藏相关部件
        if not self.mode:
            for child in self.root.children.values():
                if child != self.label:
                    child.grid_remove()
            self.root.geometry('+{}+{}'.format(self.x, self.y + 20))

        self.run_service()
        self.root.mainloop()

    def start(self):
        """开始执行，根据命令行参数，决定是后台执行还是启动界面"""
        self.get_config()
        if len(sys.argv) == 1:
            self.run_gui()
        else:
            self.run_service()


if __name__ == "__main__":
    Remote().start()
