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

import re
import sys
import threading
import tkinter as tk

import qrcode

from service import run_flask
from toolbox import config


class Remote(object):
    def __init__(self):
        """给软件设置初始参数"""
        self.x_relative = 0  # 相对坐标x
        self.y_relative = 0  # 相对坐标y
        # 颜色分别是：主界面，按钮边框，消息提示框(按钮hover色)，文字，二维码前景色，二维码背景色
        self.skins = [('#1F2326', 'black', '#1F2336', '#00ffff', '#1F2326',  '#00ffff'),
                      ('#FFFFFF', '#90ee90', '#D0D0D0',
                       '#00ced1', '#00ced1', '#FFFFFF')
                      ]
        self.button_list = []  # 按钮列表
        self.entry = None  # 文本框对象
        self.entry_content = ""
        self.root = None
        self.label = None
        self.img_label = None
        self.close_button_label = None
        self.img_close = None
        self.img_close_hover = None

    def run_service(self):
        """运行服务器"""
        thr = threading.Thread(target=run_flask, args=(self.label, self.root))
        thr.daemon = True
        thr.start()

    def generate_qrcode(self):
        '''生成二维码'''
        qr = qrcode.QRCode(box_size=4, border=0)
        qr.add_data(
            "http://{}:8765/?match={}".format(config.ip, config.match_code))
        img = qr.make_image(
            fill_color=self.skins[config.skin][4], back_color=self.skins[config.skin][5])
        img.save('qrcode.png')
        self.qrcode = tk.PhotoImage(file="qrcode.png")
        self.img_label["image"] = self.qrcode

    def validate(self, *args):
        '''验证输入框数据'''
        data = self.entry_content.get()
        if not re.match(r"^[0-9a-zA-Z\_\-]{0,10}$", data):
            self.label.config(text='输入不合法')
            self.entry_content.set(config.match_code)
        else:
            config.match_code = data
            self.generate_qrcode()
            self.label.config(text='已更新匹配码')

    def mini_mode(self, e):
        """切换界面显示模式"""
        config.mode = 0 if self.img_label.winfo_ismapped() else 1
        if config.mode:
            for child in self.root.children.values():
                if child != self.label:
                    child.grid()
            self.root.geometry('+{}+{}'.format(config.x, config.y))
        else:
            for child in self.root.children.values():
                if child != self.label:
                    child.grid_remove()
            self.root.geometry('+{}+{}'.format(config.x, config.y + 20))

    def change_skin(self):
        """切换皮肤"""
        config.skin = (config.skin + 1) % len(self.skins)
        self.generate_qrcode()
        self.root["bg"] = self.skins[config.skin][0]
        self.label["fg"] = self.skins[config.skin][3]
        self.label["bg"] = self.skins[config.skin][2]
        self.entry["fg"] = self.skins[config.skin][3]
        self.entry["bg"] = self.skins[config.skin][0]
        self.img_label["fg"] = self.skins[config.skin][3]
        self.img_label["bg"] = self.skins[config.skin][5]
        self.close_button_label["fg"] = self.skins[config.skin][3]
        self.close_button_label["bg"] = self.skins[config.skin][0]
        for bt in self.button_list:
            bt["fg"] = self.skins[config.skin][3]
            bt["bg"] = self.skins[config.skin][0]
            bt["activebackground"] = self.skins[config.skin][2]
            bt["activeforeground"] = self.skins[config.skin][3]
            bt["highlightbackground"] = self.skins[config.skin][1]

    def quit(self, e):
        config.x = self.root.winfo_x()
        config.y = self.root.winfo_y()
        config.save_config()
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
            config.x = new_x
            config.y = new_y
            self.root.geometry('+{}+{}'.format(config.x, config.y))

    def click(self, e):
        '''左键单击窗口时获得鼠标位置，辅助移动窗口'''
        self.x_relative = e.x
        self.y_relative = e.y

    def run(self):
        """启动软件主界面"""
        self.root = tk.Tk()
        self.root.title('')
        img = tk.PhotoImage(file=sys.path[0] + '/assets/ICON.png')
        self.root.tk.call('wm', 'iconphoto', self.root._w, img)
        # 主窗口
        if config.x == config.y == 0:
            config.x = self.root.winfo_screenwidth() // 2 - 100
            config.y = self.root.winfo_screenheight() // 2 - 200
        self.root.geometry('+{}+{}'.format(config.x, config.y))
        self.root["background"] = self.skins[config.skin][0]
        self.root.resizable(False, False)  # 固定窗口大小
        self.root.overrideredirect(True)  # 去掉标题栏
        self.root.bind('<Button-1>', self.click)
        self.root.bind('<B1-Motion>', self.move)
        # 标题栏及关闭按钮
        self.img_close = tk.PhotoImage(
            file=sys.path[0] + "/assets/titlebutton-close.png")
        self.img_close_hover = tk.PhotoImage(
            file=sys.path[0] + "/assets/titlebutton-close-hover.png")
        self.close_button_label = tk.Label(self.root, image=self.img_close, width=20,
                                           height=20, fg=self.skins[config.skin][3], bg=self.skins[config.skin][0])
        self.close_button_label.grid(column=1, ipadx=2, sticky=tk.E)
        self.close_button_label.bind('<ButtonPress-1>', self.quit)  # 添加单击事件
        self.close_button_label.bind('<Enter>', self.change_close_button_img)
        self.close_button_label.bind('<Leave>', self.change_close_button_img)
        # 消息框
        self.label = tk.Label(self.root, text='消息框', bg=self.skins[config.skin][2], fg=self.skins[config.skin][3], font=(
            "Arial, 12"), relief=tk.FLAT, width=19)
        self.label.grid(ipady=2, column=0, columnspan=2, row=1)
        self.label.bind('<Double-Button-1>', self.mini_mode)  # 添加双击事件
        self.label.bind('<Button-3>', self.quit)
        # 按钮组(方便以后加按钮)
        button_configs = [
            ('切换主题', self.change_skin, 1, 2),
        ]
        for bc in button_configs:
            button = tk.Button(self.root, text=bc[0], relief=tk.FLAT, command=bc[1], highlightthickness=0.5, fg=self.skins[config.skin][3], bg=self.skins[config.skin]
                               [0], activebackground=self.skins[config.skin][2], activeforeground=self.skins[config.skin][3], highlightbackground=self.skins[config.skin][1])
            button.grid(column=bc[2], row=bc[3], padx=3,
                        pady=3, sticky=tk.N + tk.E + tk.S + tk.W)
            self.button_list.append(button)
        # 输入框
        self.entry_content = tk.StringVar()
        self.entry = tk.Entry(self.root, fg=self.skins[config.skin][3], bg=self.skins[config.skin][0], width=10, textvariable=self.entry_content, justify=tk.CENTER,
                              highlightthickness=0.5, highlightbackground='#4F4F4F', highlightcolor='#4F4F4F', insertbackground=self.skins[config.skin][3], relief=tk.FLAT)
        self.entry_content.set(config.match_code)
        self.entry_content.trace_add("write", self.validate)
        self.entry.grid(column=0, row=2, padx=3, pady=3,
                        sticky=tk.N + tk.E + tk.S + tk.W)

        # 二维码界面
        self.img_label = tk.Label(self.root, width=120, height=120,
                                  fg=self.skins[config.skin][3], bg=self.skins[config.skin][5])
        self.generate_qrcode()
        self.img_label.grid(column=0, columnspan=2, row=6, pady=8)
        # 迷你模式时隐藏相关部件
        if not config.mode:
            for child in self.root.children.values():
                if child != self.label:
                    child.grid_remove()
            self.root.geometry('+{}+{}'.format(config.x, config.y + 20))

        self.run_service()
        self.root.mainloop()


if __name__ == "__main__":
    Remote().run()
