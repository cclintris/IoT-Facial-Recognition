import socket

import time, re, websocket, json, threading, requests, base64, io
from bs4 import BeautifulSoup as bs
import MyUtil,FaceRec
from PIL import Image, ImageFile

# 注意，该工程下所有py均部署在atlas200dk板子上

CloudServerUrl = None
ViewServerUrl = "http://192.168.244.166:7003"
DataServerUrl = "ws://192.168.244.166:7003"
DataServerBiosUrl = None
rogerWs: websocket.WebSocketApp = None
CurrentTimeStamp: int = 0
b64Str = None


# 压缩base64的图片
def compress_image_bs64(b64, mb, k) :
    f = base64.b64decode(b64)
    with io.BytesIO(f) as im :
        o_size = len(im.getvalue()) // 1024
        if o_size <= mb :
            return b64
        im_out = im
        while o_size > mb :
            img = Image.open(im_out)
            x, y = img.size
            out = img.resize((int(x * k), int(y * k)), Image.ANTIALIAS)
            im_out.close()
            im_out = io.BytesIO()
            out.save(im_out, 'jpeg')
            o_size = len(im_out.getvalue()) // 1024
        b64 = base64.b64encode(im_out.getvalue())
        im_out.close()
        return str(b64, encoding='utf8')


def pushToCloud(data) :
    global CurrentTimeStamp, b64Str, rogerWs
    # 确保使用时三者已正确初始化

    json_data = json.loads(data)
    if json_data['type'] != 'video' :
        return
    data_to_send = {}
    data_to_send['timeSeq'] = str(CurrentTimeStamp)
    CurrentTimeStamp += 1
    # img_bs64_data = json_data['image']
    img_bs64_data = compress_image_bs64(json_data['image'], 20, 0.9)
    data_to_send['dataBuf'] = str(img_bs64_data)
    b64Str = data_to_send['dataBuf']
    # print(str("data:image/jpeg;base64," + data_to_send['dataBuf']))
    data_to_send = json.dumps(data_to_send)

    rogerWs.send(data_to_send)


def start(ch) :
    global ViewServerUrl, DataServerBiosUrl,CloudServerUrl

    if(ch!=''):
        CloudServerUrl = "ws://%s:8097/iot/roger"%ch

    response = requests.get(ViewServerUrl + "/view", {"name" : "xgs"})
    html = response.content
    bsObj = bs(html, "html.parser")

    script_list = bsObj.find_all("script")
    main_js_script_content: str = str(script_list[1].contents[0])

    try :
        js_lines = main_js_script_content.split("\n")
        for line in js_lines :
            match_list = re.match("var wsUrl =.+", line)
            if (match_list is None) :
                pass
            else :
                tmp = re.search("\".+\"", line)[0]
                DataServerBiosUrl = tmp[1 :len(tmp) - 1]
                print("fetch BiosUrl")
                print(DataServerBiosUrl)
                # eg "/websocket?req=0.556667815718458&name=xgs"
                break
    except :
        print('fetch BiosUrl failure')

    # 建立与本地ViewServer的ws连接，并开始拉取视频流
    def CrawlerThread() :
        global DataServerUrl
        DataServerUrl = DataServerUrl + DataServerBiosUrl

        # eg "ws://192.168.244.166:7003/websocket?req=0.4947688084075008&name=xgs"
        def on_open(ws) :
            print("crawler OnOpen")
            ws.send('next')

        def on_message(ws, msg) :
            # print("OnMsg")
            # pushToCloud中通过另一个ws与云服务器进行消息交互，向云服务器推流
            if(CloudServerUrl is not None):
                pushToCloud(msg)
            # print("send dataBuf")
            ws.send("next")

        def on_error(ws, error) :
            print("crawler OnError")
            print(error)

        def on_close(ws) :
            print("crawler OnClose")

        crawlWs = websocket.WebSocketApp(DataServerUrl, on_open=on_open, on_message=on_message, on_error=on_error,
                                         on_close=on_close)
        print("建立crawlWS")
        crawlWs.run_forever()

    # 建立与云服务器的ws连接，开始推送视频流
    def RogerThread() :
        global rogerWs, b64Str, CloudServerUrl

        def on_open(ws) :
            print("roger OnOpen")

        def on_message(ws, msg) :
            if (msg == "photo") :
                print("remote req take photo")
                # print(b64Str)

                def recall(info) :
                    print("info send to roger is " + info[1])
                    ws.send(info[1])

                # print("假装执行了人脸识别")
                FaceRec.doFaceRec(b64Str, recall=recall, compressAimKB=20)

        def on_error(ws, error) :
            print("roger OnError")
            print(error)

        def on_close(ws) :
            print("roger OnClose")

        rogerWs = websocket.WebSocketApp(CloudServerUrl, on_open=on_open, on_message=on_message, on_error=on_error,
                                         on_close=on_close)
        print("建立rogerWs")
        rogerWs.run_forever()

    global CurrentTimeStamp
    CurrentTimeStamp = int(time.time() * (10 ** 6))

    if CloudServerUrl is not None:
        threading.Thread(target=RogerThread).start()
    threading.Thread(target=CrawlerThread).start()


if __name__ == "__main__" :
    start('123.57.200.185')
    while True:
        time.sleep(1)
    # threading.Thread(target=CrawlerTest).start()
