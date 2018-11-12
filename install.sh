#!/bin/bash
echo -n "请输入你的系统名(arch/deepin):"
read system 
if test $system = "deepin"
then
    sudo apt-get install python3-pip 
    sudo apt-get install python3-tk 
    sudo pip3 install flask 
    sudo pip3 install qrcode[pil] 
    sudo pip3 install -U flask-cors 
    sudo pip3 install PyUserInput 
    sudo pip3 install setproctitle 
    python3 remote.py 
    clear 
echo "安装完成，请从启动器打开软件"
else
    sudo pacman -S python-pip 
    sudo pacman -S python-pmw 
    sudo pip3 install flask 
    sudo pip3 install qrcode[pil] 
    sudo pip3 install -U flask-cors 
    sudo pip3 install PyUserInput 
    sudo pip3 install setproctitle 
    python3 remote.py 
    clear 
echo "安装完成，请从启动器打开软件"
fi
