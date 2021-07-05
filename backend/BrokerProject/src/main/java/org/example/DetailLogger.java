package org.example;

import org.springframework.cloud.gateway.filter.GatewayFilterChain;
import org.springframework.cloud.gateway.filter.GlobalFilter;
import org.springframework.core.Ordered;
import org.springframework.http.server.reactive.ServerHttpRequest;
import org.springframework.stereotype.Component;
import org.springframework.web.server.ServerWebExchange;
import reactor.core.publisher.Mono;

import java.util.logging.Logger;

@Component
public class DetailLogger implements GlobalFilter, Ordered {

    static Logger logger = Logger.getLogger("logger");

    @Override
    public Mono<Void> filter(ServerWebExchange exchange, GatewayFilterChain chain) {
        String toLog = "\n";
        ServerHttpRequest req = exchange.getRequest();

        toLog += "uri: " + req.getURI().toString() + "\n";
        toLog += "from address: " + req.getRemoteAddress() + "\n";
        toLog += "query params: " + req.getQueryParams();
        logger.info(toLog);

        return chain.filter(exchange.mutate().build());
    }

    @Override
    public int getOrder() {
        return -199;
    }
}
