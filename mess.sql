CREATE TABLE IF NOT EXISTS support_messages (
    id         SERIAL       PRIMARY KEY,
    user_id    INTEGER      REFERENCES users(id) ON DELETE SET NULL,
    name       VARCHAR(100) NOT NULL,
    email      VARCHAR(150) NOT NULL,
    subject    VARCHAR(100) DEFAULT 'General Inquiry',
    message    TEXT         NOT NULL,
    is_read    BOOLEAN      NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP
);