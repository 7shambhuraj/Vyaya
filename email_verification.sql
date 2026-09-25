
ALTER TABLE users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN NOT NULL DEFAULT FALSE;


UPDATE users SET is_verified = TRUE WHERE is_verified = FALSE;


SELECT id, name, email, is_verified, is_active FROM users LIMIT 10;
