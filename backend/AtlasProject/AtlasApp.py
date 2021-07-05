import json, os, threading,argparse,warnings
from flask import Flask, render_template, redirect, request, url_for, make_response, jsonify
from flask_restful import Resource, Api, reqparse
import CrawlerAndRoger, FaceRec, MyUtil

# 此py部署在atlas200dk上
warnings.filterwarnings("ignore")
parser=argparse.ArgumentParser()
parser.add_argument('-dh',help='dev use host', required=True)
parser.add_argument('-dp',help='dev use port', required=True)
parser.add_argument('-eh',help='edgex use host', required=True)
parser.add_argument('-ch',help='gate broker', required=True)

args=vars(parser.parse_args())

HOST  = args["dh"]
PORT  = args["dp"]
EDGEX_IP = args['eh']
CLOUD_IP = args['ch']

app = Flask(__name__)


def Registry() :
    MyUtil.bindEdgeXHost(EDGEX_IP)
    MyUtil.regis("las", "camera", "las_profile.yaml", HOST, PORT)
    MyUtil.createStream()
    MyUtil.createRule("button", MyUtil.ON, "http://%s:%s%s" % (HOST, PORT, BE_REQ_URL))


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


BE_REQ_URL = '/atlas/camera'


WATING = False
# 接到请求，执行“拍照-人脸识别“流程
@app.route(BE_REQ_URL, methods=['GET'])
def getReq() :
    global WATING
    if(WATING):
        print("设备占用中")
        return "BAD", 204
    WATING = True
    print("开始拍照-人脸识别")

    def recall(data) :
        # predict后的回调
        res = data[0]
        if res<1:
            MyUtil.Touch("las","camera",MyUtil.ON)
        else :
            MyUtil.Touch("las","camera",MyUtil.OFF)

        MyUtil.Touch("las","camera",MyUtil.NOR)
        global WATING
        WATING = False
        print("识别结果已传回EDGEX")

    # 为了提高效率，这里我们直接开一条新线程，异步返回结果
    FaceRec.doFaceRec(CrawlerAndRoger.b64Str, recall=recall, compressAimKB=20)

    return "OK", 200


if __name__ == "__main__" :
    try :
        CrawlerAndRoger.start(CLOUD_IP)
        print("数据源和推送目标准备就绪")
    except :
        print("数据源和推送目标出现问题")
    try :
        Registry()
        print("阿特拉斯在EdgeX注册成功")
    except :
        print("阿特拉斯在EdgeX注册失败")
    app.run(debug=False, host=HOST, port=int(os.getenv('PORT', PORT)), threaded=True)
