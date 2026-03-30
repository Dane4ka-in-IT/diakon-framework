package dev.diakon.nocodeplatform.controllers;

import dev.diakon.nocodeplatform.entity.User;
import dev.diakon.nocodeplatform.service.UserService;
import lombok.Data;
import lombok.NonNull;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/users")
@RequiredArgsConstructor
public class UserController {
    private final UserService userService;

    @Data
    public static class LoginRequest {
        private String email;
        private String password;
    }

    @PostMapping("/register")
    public ResponseEntity<@NonNull String> register(@RequestBody User user) {
        user.setIsPremium(false);
        userService.registerUser(user);
        return ResponseEntity.ok("Пользователь успешно зарегистрирован");
    }

    @PostMapping("/login")
    public ResponseEntity<@NonNull User> login(@RequestBody LoginRequest request) {
        User user = userService.loginUser(request.getEmail(), request.getPassword());
        return ResponseEntity.ok(user);
    }

    @PatchMapping("/{userId}/premium")
    public ResponseEntity<@NonNull String> upgradeToPremium(@PathVariable Long userId) {
        userService.togglePremium(userId);
        return ResponseEntity.ok("Статус премиума успешно обновлен!");
    }
}
