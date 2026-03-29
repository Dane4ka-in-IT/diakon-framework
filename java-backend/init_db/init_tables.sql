create table users(
    id BIGSERIAL PRIMARY KEY,
    user_name varchar(20),
    user_password varchar(100),
    is_premium bool
)