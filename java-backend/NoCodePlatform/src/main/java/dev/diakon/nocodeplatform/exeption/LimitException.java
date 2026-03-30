package dev.diakon.nocodeplatform.exeption;

import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.ResponseStatus;

@ResponseStatus(HttpStatus.BAD_REQUEST)
public class LimitException extends RuntimeException {
    public LimitException(String message) {
        super(message);
    }
}
