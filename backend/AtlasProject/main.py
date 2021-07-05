
import base64
from io import BytesIO
import os
import sys
import socket
import threading
from PIL import Image, ImageFile
from facenet import Facenet
import time
gallery_path_list = []
model = Facenet()
ImageFile.LOAD_TRUNCATED_IMAGES = True

for root, dirs, files in os.walk("data/gallery", topdown=False):
    for name in files:
        gallery_path_list.append(os.path.join(root, name))


def facePredict(fileInfo, output_path):
    # try:
    output_message = ""
    lowest_distance = 100
    lowest_index = -1
    print(f"[INFO]开始匹配")
    with open("data/tmp/tmp.jpg", "wb") as f:
        f.write(fileInfo)
    time.sleep(1)
    for i in range(len(gallery_path_list)):
        image_1 = Image.open("data/tmp/tmp.jpg")
        image_2 = Image.open(gallery_path_list[i])
        # test_name = gallery_path_list[i].split('\\')[-1].split('.')[0]
        test_name = gallery_path_list[i].split('/')[-1].split('.')[0]
        probability = model.detect_image(image_1, image_2)
        print(f"[INFO]欧氏距离：{test_name}：{probability}的匹配")
        if probability < lowest_distance:
            lowest_distance = probability
            lowest_index = i
    # user_name = gallery_path_list[lowest_index].split("/")[-1].split(".")[0]
    user_name = gallery_path_list[lowest_index].split("\\")[-1].split(".")[0]
    output_message += f"{user_name} {lowest_distance[0]}"
    return output_message
    # except Exception as e:
    #     output_message = "ERROR"
    # with open(output_path, "w", encoding="utf-8") as f:
    #     f.write(output_message)
    # print(f"[INFO]完成，结果输出到了{output_path}中")


def connection():
    s = socket.socket()
    host = "0.0.0.0"
    port = 10001
    s.bind((host, port))
    s.listen(5)
    while True:
        c, addr = s.accept()
        print("[INFO]已连接")
        while True:
            # try:
            # pic = c.recv(500000)
            cmd_res_size = c.recv(1024)  # 接收命令的长度
            print("命令结果大小：", cmd_res_size.decode('utf-8'))
            recevied_size = 0  # 接收客户端发来数据的计算器
            recevied_data = b''  # 客户端每次发来内容的计数器
            c.send(b'1')
            while recevied_size < int(cmd_res_size.decode('utf-8')):  # 当接收的数据大小 小于 客户端发来的数据
                cmd_res = c.recv(1024)
                recevied_size += len(cmd_res)  # 每次收到的服务端的数据有可能小于1024，所以必须用len判断
                recevied_data += cmd_res
            # with open(f"./data/input/{time.time()}.jpg", "wb") as f:
            #     f.write(pic)
            output_msg = facePredict(recevied_data, None)
            c.send(output_msg.encode("utf-8"))
            c.close()
            break
            # except:
            #     print("[ERROR]连接中断！")
            #     c.close()
            #     break


if __name__ == '__main__':
    # with open("./data/gallery/1.png", "rb") as f:
    #     facePredict(f.read(),None)
    # with open("./data/gallery/2.png", "rb") as f:
    #     facePredict(f.read(),None)
    connection()
    # input_pic_path = sys.argv[1]
    # output_txt_path = sys.argv[2]
    # facePredict(input_pic_path, output_txt_path)
