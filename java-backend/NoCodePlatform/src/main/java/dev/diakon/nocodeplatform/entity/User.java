package dev.diakon.nocodeplatform.entity;

import jakarta.persistence.*;
import jakarta.validation.constraints.NotNull;
import jakarta.validation.constraints.Size;
import lombok.Getter;
import lombok.Setter;
import org.hibernate.annotations.ColumnDefault;

@Getter
@Setter
@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    @Column(name = "id", nullable = false)
    private Long id;

    @Size(max = 50)
    @NotNull
    @Column(name = "user_name", nullable = false, length = 50)
    private String userName;

    @Size(max = 50)
    @NotNull
    @Column(name = "user_email", nullable = false, length = 50)
    private String userEmail;

    @Size(max = 100)
    @NotNull
    @Column(name = "user_password", nullable = false, length = 100)
    private String userPassword;

    @ColumnDefault("false")
    @Column(name = "is_premium")
    private Boolean isPremium;
}