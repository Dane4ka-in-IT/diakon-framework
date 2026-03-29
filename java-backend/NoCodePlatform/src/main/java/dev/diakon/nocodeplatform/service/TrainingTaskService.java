package dev.diakon.nocodeplatform.service;

import dev.diakon.nocodeplatform.entity.TrainingTask;
import dev.diakon.nocodeplatform.repositiry.TrainingTaskRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class TrainingTaskService {
    private final TrainingTaskRepository trainingTaskRepository;

    public void save(TrainingTask trainingTask) {
        trainingTaskRepository.save(trainingTask);
        System.out.println("Задача успешно сохранена в базу данных!");
    }


}
