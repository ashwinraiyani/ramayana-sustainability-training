-- PostgreSQL Database Schema

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE modules (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    theme VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE module_progress (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    module_id INT REFERENCES modules(id),
    progress DECIMAL(5,2) CHECK (progress >= 0 AND progress <= 100),
    completed_at TIMESTAMP
);

CREATE TABLE chat_messages (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    message_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE assessments (
    id SERIAL PRIMARY KEY,
    module_id INT REFERENCES modules(id),
    question TEXT NOT NULL,
    correct_answer TEXT NOT NULL
);

CREATE TABLE badges (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    badge_name VARCHAR(50),
    awarded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_user_username ON users(username);
CREATE INDEX idx_module_title ON modules(title);
CREATE INDEX idx_progress_user ON module_progress(user_id);
CREATE INDEX idx_chat_user ON chat_messages(user_id);
