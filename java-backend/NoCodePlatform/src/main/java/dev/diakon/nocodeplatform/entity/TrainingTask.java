package dev.diakon.nocodeplatform.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.Setter;
import org.hibernate.annotations.JdbcTypeCode;
import org.hibernate.type.SqlTypes;

import java.time.Instant;
import java.util.Map;

@Getter
@Setter
@Entity
@Table(name = "training_tasks")
public class TrainingTask {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id", nullable = false)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id")
    private User user;

    @Size(max = 20)
    @Column(name = "dataset_name", length = 20)
    private String datasetName;

    @Size(max = 20)
    @Column(name = "optimizer", length = 20)
    private String optimizer;

    @Size(max = 20)
    @Column(name = "status", length = 20)
    private String status;

    @Column(name = "learning_rate")
    private Double learningRate;

    @Column(name = "epochs")
    private Integer epochs;

    @Column(name = "layers_config")
    @JdbcTypeCode(SqlTypes.JSON)
    private Map<String, Object> layersConfig;

    @Column(name = "loss_history", length = Integer.MAX_VALUE)
    private String lossHistory;

    @Column(name = "start_time")
    private Instant startTime;

    @Column(name = "end_time")
    private Instant endTime;
}