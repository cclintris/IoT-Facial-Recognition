package org.example;

import org.springframework.stereotype.Component;
import redis.clients.jedis.Jedis;
import redis.clients.jedis.params.SetParams;

@Component
public class RedisUtil {
    private final Jedis jedis;

    public RedisUtil() {
        jedis = new Jedis("localhost", 6379);
        jedis.flushAll();
        jedis.set("BUTTON","0");
    }

    public synchronized boolean set(String key, String value, long time) {
        SetParams params = new SetParams();
        params.ex(time);
        String ex = jedis.set(key, value, params);
        return !(ex == null);
    }

    public synchronized boolean set(String key, String value) {
        String ex = jedis.set(key, value);
        return !(ex == null);
    }

    public synchronized String get(String key) {
        return jedis.get(key);
    }

    public synchronized boolean del(String key) {
        return jedis.del(key) == 1L;
    }
}
