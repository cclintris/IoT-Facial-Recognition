# -*- coding: utf-8

import base64
import os
import socket
import time

import requests


def bs64ToBytes(bs64Str):
    return base64.b64decode(bs64Str)

cmdUrl = "http://123.57.200.185:8097/iot/roger/cmd"

def keep_ask():
    while True:
        time.sleep(0.5)
        code = requests.get(cmdUrl, params={"code": '0', "info": ""}).text
        if code == '0':
            continue
        elif code == '1':
            print("[INFO]按钮被按下")
            requests.get(cmdUrl, params={"code": '1', "info": ""})
            # os.system("$HOME/ascendcamera/out/main -i -c 1 -o ./temp/filename.jpg --overwrite")
            # with open("./temp/filename.jpg", "rb") as f:
            #     pic_info = f.read()
            info = predict()
            requests.get(cmdUrl, params={"code": '2', "info": info})
            time.sleep(1)


def predict():
    # pic_info = bs64ToBytes(pic_info)
    s = socket.socket()
    host = "192.168.244.2"
    port = 10001
    s.connect((host, port))
    s.send(b'go')
    result = s.recv(1024).decode("utf-8")
    print(result)
    return result


if __name__ == '__main__':
    keep_ask()
