import React, { useState, useEffect, useRef } from "react";
import "../styles/StreamingVideo.css";
import { Button, Form, Input, Divider, message } from "antd";
import ParticlesBg from "particles-bg";
import {
  LoadingOutlined,
  DownloadOutlined,
  VideoCameraOutlined,
} from "@ant-design/icons";
import $ from "jquery";

const StreamingVideo = () => {
  $(".loading").hide();

  // global websocket instance
  const ws = useRef();

  const [name, setName] = useState("人名");
  const [euler, setEuler] = useState("欧拉相似度");
  const [safe, setSafe] = useState("安全");

  useEffect(() => {
    let wsProtocol = "ws://";
    if (window.location.protocol === "https:") {
      wsProtocol = "wss://";
    }
    let wsUrl = wsProtocol + "123.57.200.185:8097/iot/camera";

    ws.current = new WebSocket(wsUrl);
    // console.log("websocket instance", ws.current);

    ws.current.onopen = () => {
      console.info("websocket connetion initiated");
      // setInterval(() => {
      //   ws.current.send("next")
      // }, 1000)
    };
    ws.current.onclose = () => {
      console.warn("websocket connection terminated");
    };
    ws.current.onerror = () => {
      console.error("websocket connection errored");
    };
  });

  useEffect(() => {
    const canvas = document.getElementById("atlas");
    const ctx = canvas.getContext("2d");
    ctx.strokeRect(0, 0, 900, 450);
    $(".loading").hide();
    startViewVideo(canvas, ctx);

    return () => {
      ws.current.close();
    };
  });

  const startViewVideo = (canvas, ctx) => {
    $(".canvas").hide();

    // let onmessageflag = false;
    // let count = 0;
    // let timestart = 0;

    ws.current.onopen = function () {
      ws.current.send("next");
    };
    ws.current.onmessage = function (evt) {
      // console.log("startViewVideo data received", evt.data);
      if (evt.data.length > 200) {
        // $(".loading").hide();
        $(".canvas").show();
        let data = evt.data;
        let src = "data:image/jpeg;base64," + data;
        let img = new Image();
        img.src = src;
        img.width = "600";
        img.height = "400";
        // canvas.width = 600;
        // canvas.height = 400;
        img.onload = function () {
          ctx.drawImage(img, 0, 0, 600, 400);
        };
        ws.current.send("next");
      }
    };
  };

  const downloadlink = (url) => {
    let fakelink = document.createElement("a");
    fakelink.download = "picture"; // 设置下载的文件名，默认是'下载'
    fakelink.href = url;
    document.body.appendChild(fakelink);
    fakelink.click();
    fakelink.remove(); // 下载之后把创建的元素删除
  };

  const saveAsPNG = (canvas) => {
    return canvas.toDataURL("image/png");
  };

  const download = () => {
    message.success("下载照片成功！");
    const canvas = document.getElementById("atlas");
    downloadlink(saveAsPNG(canvas));
  };

  const shoot = () => {
    // console.log("shoot");
    ws.current.send("photo");
    message.success("拍照成功！");
    $(".loading").show();
    ws.current.onmessage = (evt) => {
      if (evt.data.length < 200) {
        const res = evt.data.split(" ");
        // console.log("shoot", res);
        setName(res[0]);
        setEuler(res[1]);
        $(".loading").hide();
      }
    };
  };

  return (
    <>
      <div className="streamingV">
        <span
          style={{
            fontSize: "40px",
            marginBottom: "20px",
            fontFamily: "fantasy",
            color: "rgb(29, 161, 242)",
          }}
        >
          IoT Atlas 人脸识别系统
        </span>
        <LoadingOutlined spin className="loading" />
        <canvas id="atlas" width="600" height="400" className="canvas"></canvas>
        <div className="btn-layout">
          <Button
            type="dashed"
            className="btn"
            onClick={download}
            icon={<DownloadOutlined />}
          >
            下载照片
          </Button>
          <Button
            type="primary"
            className="btn"
            // shape="round"
            style={{ marginLeft: "20px" }}
            onClick={shoot}
            icon={<VideoCameraOutlined />}
          >
            拍照
          </Button>
        </div>
      </div>
      <div className="recogRes">
        <div
          style={{
            height: "12%",
            color: "whitesmoke",
            textAlign: "center",
            fontSize: "25px",
          }}
        >
          人脸识别结果
        </div>
        <Form size="large">
          <Form.Item label="识别人名" name="name">
            <Input placeholder={name} />
          </Form.Item>
          <Form.Item label="相似程度" name="euler">
            <Input placeholder={euler} />
          </Form.Item>
          <Form.Item label="安全用户" name="security">
            <Input placeholder={safe} />
          </Form.Item>
        </Form>
        <Divider style={{ backgroundColor: "white" }} />
        <div className="description">
          以华为Atlas板为摄像头，采集流媒体视频，上传到云服务器，并应用Atlas
          ML算法和计算机视觉，在前端显示流媒体视频，具有人脸识别功能。
        </div>
      </div>
      <ParticlesBg
        type="polygon"
        bg={{
          position: "absolute",
          zIndex: "none",
          top: 0,
          left: 0,
        }}
      />
    </>
  );
};

export default StreamingVideo;
