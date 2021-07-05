package org.example;

import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.logging.Logger;

@Component
public class DateLogger implements GlobalFilter, Ordered {

    static Logger logger = Logger.getLogger("logger");

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        //这是在pre阶段进行拦截
        logger.info("\ndate: " + new SimpleDateFormat("yyyy-MM-dd-hh-mm-ss").format(new Date()));
        return chain.filter(exchange.mutate().build());
    }

    //order越小，优先级越高
    @Override
    public int getOrder() {
        return -200;
    }
}
