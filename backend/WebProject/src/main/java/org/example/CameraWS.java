package org.example;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;

import javax.websocket.*;
import javax.websocket.server.ServerEndpoint;
import java.util.logging.Logger;

@Controller
@ServerEndpoint(value = "/iot/camera")
public class CameraWS {

    static SeqCounter sc;
    static Logger logger = Logger.getLogger("");
    static RedisUtil redisUtil;
    static StaticPool staticPool;
    static Session currentSession;

    @Autowired
    public void init(RedisUtil redisUtil,StaticPool staticPool,SeqCounter sc) {
        CameraWS.redisUtil = redisUtil;
        CameraWS.staticPool = staticPool;
        CameraWS.sc = sc;
    }

    @OnOpen
    public void onOpen(Session session){
        logger.info("onOpen");
        currentSession = session;
        staticPool.put(session,"camera");
    }

    @OnMessage
    public void onMessage(Session session, String msg){
        logger.info("onMessage");
        if(msg.equals("photo")) {
            logger.info("get cmd \"photo\", send msg to VM node");
            rogerReply("photo");
        }
        else if(msg.equals("next")){
            logger.info("get cmd \"next\"");
            int presentSeq = sc.getPresent();
            String dataBuf = redisUtil.get("DBS:"+presentSeq);
            if(dataBuf==null)
                logger.info("dataBuf is null");
            else {
                reply(dataBuf);
                logger.info("send dataBuf to client");
            }
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

    public void rogerReply(String msg) {
        staticPool.get(Session.class,"roger").getAsyncRemote().sendText(msg);
    }
}


