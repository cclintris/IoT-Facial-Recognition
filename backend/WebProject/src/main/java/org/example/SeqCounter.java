package org.example;

import org.springframework.stereotype.Component;

import java.util.concurrent.atomic.AtomicInteger;

@Component
public class SeqCounter {
    private final AtomicInteger PresentSeq = new AtomicInteger();

    public void setPresent(int presentSeq) {
        PresentSeq.set(presentSeq);
    }

    public int getPresent() {
        return PresentSeq.get();
    }
}
