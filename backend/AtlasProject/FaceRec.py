import threading,base64,io
from PIL import Image, ImageFile
from facenet import Facenet
import time
import os


gallery_path_list = []
model = Facenet()
ImageFile.LOAD_TRUNCATED_IMAGES = True

for root, dirs, files in os.walk("data/gallery", topdown=False):
    for name in files:
        gallery_path_list.append(os.path.join(root, name))

class PredictThread(threading.Thread):
    def __init__(self,  *args, **kwargs):
        super(PredictThread, self).__init__(*args, **kwargs)
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        print("begin run the child thread")
        while True:
            print("sleep 1s")
            time.sleep(1)
            if self.stopped():
                # 做一些必要的收尾工作
                break



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


# b64转二进制
def bs64ToBytes(bs64Str) :
    return base64.b64decode(bs64Str)


def predict(pic_bytes) :
    print("收到照片数据，开始人脸识别")
    try:
        output_message = ""
        lowest_distance = 100
        lowest_index = -1
        print(f"[INFO]开始匹配")
        with open("data/tmp/tmp.jpg", "wb") as f:
            f.write(pic_bytes)
        time.sleep(1)
        for i in range(len(gallery_path_list)):
            image_1 = Image.open("data/tmp/tmp.jpg")
            image_2 = Image.open(gallery_path_list[i])
            test_name = gallery_path_list[i].split('\\')[-1].split('.')[0]
            # test_name = gallery_path_list[i].split('/')[-1].split('.')[0]
            probability = model.detect_image(image_1, image_2)
            print(f"[INFO]欧氏距离：{test_name}：{probability}的匹配")
            if probability < lowest_distance:
                lowest_distance = probability
                lowest_index = i
        user_name = gallery_path_list[lowest_index].split("/")[-1].split(".")[0]
        # user_name = gallery_path_list[lowest_index].split("\\")[-1].split(".")[0]
        output_message += f"{user_name} {lowest_distance[0]}"
        return [lowest_distance, output_message]
    except:
        return ['NO', None]


# 暴露给外界，新建一个线程，执行人脸识别任务，结束后执行回调
def doFaceRec(b64Str, recall, compressAimKB=20) :
    # b64Str是一个未经压缩的b64字符串
    b64Str = compress_image_bs64(b64Str, compressAimKB, 0.9)

    def CameraThread() :
        # 不可变对象
        # b64Str_thread_local:str = ''.join(b64Str)
        b64Str_thread_local = b64Str

        # 长阻塞
        res = predict(bs64ToBytes(b64Str_thread_local))

        # 执行回调
        recall(res)



    new_thread = threading.Thread(target=CameraThread)
    new_thread.setDaemon(True)
    new_thread.start()
