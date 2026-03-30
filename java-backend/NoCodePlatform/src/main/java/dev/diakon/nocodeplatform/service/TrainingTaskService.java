package dev.diakon.nocodeplatform.service;

import dev.diakon.nocodeplatform.entity.TrainingTask;
import dev.diakon.nocodeplatform.entity.User;
import dev.diakon.nocodeplatform.exeption.LimitException;
import dev.diakon.nocodeplatform.repositiry.TrainingTaskRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.Instant;

import java.util.concurrent.CompletableFuture;

@Service
@RequiredArgsConstructor
public class TrainingTaskService {
    private final TrainingTaskRepository trainingTaskRepository;
    private final AiClient aiClient;

    public TrainingTask createAndStartTask(User user, AiClient.PyRequest req) {

        if (!user.getIsPremium() && req.getEpochs() > 20) {
            throw new LimitException("Бесплатно только 20 эпох! Купите премиум.");
        }

        TrainingTask trainingTask = new TrainingTask();
        trainingTask.setUser(user);
        trainingTask.setStatus("IN_PROGRESS");
        trainingTask.setLearningRate(req.getLearning_rate());
        trainingTask.setDatasetName(req.getDataset());
        trainingTask.setOptimizer(req.getOptimizer());
        trainingTask.setEpochs(req.getEpochs());
        trainingTask.setStartTime(Instant.now());

        final TrainingTask savedTask = trainingTaskRepository.save(trainingTask);
        CompletableFuture.runAsync(() -> {
            try {
                AiClient.PyResponse response = aiClient.sendTrainingRequest(req);
                savedTask.setStatus("COMPLETED");
                savedTask.setLossHistory(response.getHistory().toString());
                savedTask.setEndTime(Instant.now());
            } catch (Exception e) {
                savedTask.setStatus("FAILED");
                System.err.println("Ошибка обучения: " + e.getMessage());
            }
            trainingTaskRepository.save(savedTask);
        });

        return savedTask;
    }

    public TrainingTask getTaskById(Long id) {
        return trainingTaskRepository.findById(id)
                .orElseThrow(() -> new RuntimeException("Задача не найдена"));
    }

    public java.util.List<TrainingTask> getTasksByUserId(Long userId) {
        return trainingTaskRepository.findAllByUser_Id(userId);
    }
}