package org.example;

import org.springframework.stereotype.Component;

import java.util.HashMap;

@Component
public class StaticPool {
    private HashMap<String,Object> map = new HashMap<>();

    public <T> void put(T instance, String name){
        map.put(name,instance);
    }

    public <T> T get(Class<T> c,String name){
        return c.cast(map.get(name));
    }
}
