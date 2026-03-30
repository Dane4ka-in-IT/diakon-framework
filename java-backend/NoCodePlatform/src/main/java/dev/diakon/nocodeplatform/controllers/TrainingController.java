package dev.diakon.nocodeplatform.controllers;

import dev.diakon.nocodeplatform.entity.TrainingTask;
import dev.diakon.nocodeplatform.exeption.UserNotFound;
import dev.diakon.nocodeplatform.repositiry.UserRepository;
import dev.diakon.nocodeplatform.service.AiClient;
import dev.diakon.nocodeplatform.service.TrainingTaskService;
import lombok.NonNull;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/tasks")
@RequiredArgsConstructor
public class TrainingController {

    private final TrainingTaskService trainingTaskService;
    private final UserRepository userRepository;

    @PostMapping("/start")
    public ResponseEntity<@NonNull TrainingTask> startTask(
            @RequestParam Long userId,
            @RequestBody AiClient.PyRequest request) {

        return userRepository.findById(userId)
                .map((u) -> ResponseEntity.ok(trainingTaskService
                        .createAndStartTask(u, request)))
                .orElseThrow(() -> new UserNotFound("Пользователь не найден"));

    }

    @GetMapping("/{taskId}")
    public ResponseEntity<@NonNull TrainingTask> checkStatus(@PathVariable Long taskId) {
        return ResponseEntity.ok(trainingTaskService.getTaskById(taskId));
    }
}