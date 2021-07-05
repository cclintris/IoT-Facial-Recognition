import json, time, os, threading, requests,argparse,warnings
import MyUtil
import pyfirmata
from flask import Flask

warnings.filterwarnings("ignore")
parser=argparse.ArgumentParser()
parser.add_argument('-dh',help='dev use host', required=True)
parser.add_argument('-dp',help='dev use port', required=True)
parser.add_argument('-eh',help='edgex use host', required=True)

args=vars(parser.parse_args())

HOST  = args["dh"]
PORT  = args["dp"]
EDGEX_IP = args['eh']

app = Flask(__name__)

DEV_NAME = "/dev/ttyACM0"
BUZZ = 2
BUTTON = 10
LIGHT = 13

board = None

def InitSong() :
    global board
    board = pyfirmata.Arduino(DEV_NAME)
    it = pyfirmata.util.Iterator(board)
    it.start()
    board.digital[BUZZ].write(1)
    board.digital[LIGHT].write(0)
    board.digital[BUTTON].mode = pyfirmata.INPUT


def playBuzz(n: int, gap: int) :
    global board
    for i in range(0, n) :
        board.digital[BUZZ].write(0)
        time.sleep(gap)
        board.digital[BUZZ].write(1)
        time.sleep(gap)
    return 'sound successfully!'

lastsw = None
def checkButton() :
    global board,lastsw
    sw = board.digital[BUTTON].read()
    if lastsw is None:
        lastsw = sw
        return False
    else:
        res = lastsw!=sw
        lastsw = sw
        if res:
            board.digital[LIGHT].write(1)
        else :
            board.digital[LIGHT].write(0)
    return res

def Registry() :
    MyUtil.bindEdgeXHost(EDGEX_IP)
    MyUtil.regis("song", "button", "song_profile.yaml", HOST, PORT)
    MyUtil.createStream()
    MyUtil.createRule("camera", MyUtil.ON, "http://%s:%s%s" % (HOST, PORT, BE_REQ_URL))
    MyUtil.createRule("camera", MyUtil.OFF, "http://%s:%s%s" % (HOST, PORT, BE_REQ_URL))

# 监听按钮状态，报告给edgex
def ButtonThread() :
    while True :
        # res = checkButton()
        if checkButton() :
            print("按钮被按下")
            MyUtil.Touch("song","button",MyUtil.ON)
        else:
            MyUtil.Touch("song","button",MyUtil.NOR)
        time.sleep(0.2)

# 接收EdgeX发来的注册确认信息，完成握手
@app.route('/api/v1/device/register', methods=['POST'])
def register() :
    request.get_json(force=True)
    parser = reqparse.RequestParser()
    parser.add_argument('id', required=True)
    args = parser.parse_args()
    id = args['id']
    print("registering device: ", id)
    returnData = "Device registered"
    return returnData, 201


# 蜂鸣器的角色是响应器，不需要主动发出请求，只需要被请求，也就是BE_REQ
BE_REQ_URL = '/song/buzz'


@app.route(BE_REQ_URL, methods=['GET'])
def success() :
    playBuzz(3, 0.3)
    print("人脸相似度高，发出3声蜂鸣")
    return "OK", 201


@app.route(BE_REQ_URL, methods=['DELETE'])
def failure() :
    playBuzz(2, 0.5)
    print("人脸相似度低，发出2声蜂鸣")
    return "OK", 201


if __name__ == "__main__" :
    try :
        InitSong()
        print("奥松接入成功")
    except :
        print("奥松接入失败")
    try :
        Registry()
        print("EdgeX注册成功")
    except :
        print("EdgeX注册失败")
    try :
        time.sleep(2)
        threading.Thread(target=ButtonThread).start()
        print("开始监听按钮")
    except :
        print("监听按钮失败")
    app.run(debug=True, host=HOST, port=int(os.getenv('PORT', PORT)), threaded=True)
