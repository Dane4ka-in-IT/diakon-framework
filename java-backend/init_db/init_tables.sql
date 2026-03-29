CREATE TABLE users (
        id BIGSERIAL PRIMARY KEY,
        user_name VARCHAR(50) NOT NULL,
        user_email VARCHAR(50) NOT NULL UNIQUE,
        user_password VARCHAR(100) NOT NULL,
        is_premium BOOLEAN DEFAULT FALSE
);


CREATE TABLE training_tasks (
        id BIGSERIAL PRIMARY KEY,
        user_id BIGINT REFERENCES users(id),
        dataset_name VARCHAR(20),
        optimizer VARCHAR(20),
        status VARCHAR(20),
        learning_rate DOUBLE PRECISION,
        epochs INTEGER,
        layers_config JSONB,
        loss_history TEXT,
        start_time TIMESTAMP,
        end_time TIMESTAMP
);