package org.example;

import com.alibaba.fastjson.JSON;
import com.alibaba.fastjson.JSONObject;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;

import javax.websocket.*;
import javax.websocket.server.ServerEndpoint;
import java.util.logging.Logger;

@Controller
@ServerEndpoint(value = "/iot/roger")
public class RogerWS {

    static SeqCounter sc;
    static Logger logger = Logger.getLogger("");
    static RedisUtil redisUtil;
    static StaticPool staticPool;
    static Session currentSession;

    @Autowired
    public void init(RedisUtil redisUtil,StaticPool staticPool,SeqCounter sc) {
        RogerWS.redisUtil = redisUtil;
        RogerWS.staticPool = staticPool;
        RogerWS.sc = sc;
    }

    @OnOpen
    public void onOpen(Session session){
        logger.info("onOpen");
        currentSession = session;
        staticPool.put(session,"roger");
    }

    @OnMessage
    public void onMessage(Session session, String msg){
        logger.info("onMessage");
        if(msg.length()>=200){
            // 图片
            JSONObject jo = JSON.parseObject(msg);
            int PresentSeq = (int) (jo.getLong("timeSeq")%1000);
            sc.setPresent(PresentSeq);
            String dataBuf = jo.getString("dataBuf");
            redisUtil.set("DBS:"+PresentSeq,dataBuf,30);
            logger.info("receive dataBuf, now \"timeSeq\" is "+PresentSeq);
        }
        else {
            //消息
            cameraReply(msg);
        }
    }

    @OnError
    public void onError(Throwable error){
        logger.info("onError");
    }

    @OnClose
    public void onClose(){
        logger.info("onClose");
    }

    public void reply(String msg) {
        currentSession.getAsyncRemote().sendText(msg);
    }

    public void cameraReply(String msg) {
        staticPool.get(Session.class,"camera").getAsyncRemote().sendText(msg);
    }

}
