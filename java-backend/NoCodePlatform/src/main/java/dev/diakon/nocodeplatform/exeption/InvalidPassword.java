package dev.diakon.nocodeplatform.exeption;

import org.springframework.web.bind.annotation.ResponseStatus;

@ResponseStatus
public class InvalidPassword extends RuntimeException {
    public InvalidPassword(String message) {
        super(message);
    }
}
