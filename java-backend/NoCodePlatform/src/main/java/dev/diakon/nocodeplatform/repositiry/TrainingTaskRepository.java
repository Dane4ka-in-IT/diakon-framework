package dev.diakon.nocodeplatform.repositiry;

import dev.diakon.nocodeplatform.entity.TrainingTask;
import lombok.NonNull;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface TrainingTaskRepository extends JpaRepository<@NonNull TrainingTask, @NonNull Long> {
    List<TrainingTask> findAllByUser_Id(Long id);
}
