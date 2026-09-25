ALTER TABLE users ADD COLUMN IF NOT EXISTS is_verified BOOLEAN NOT NULL DEFAULT FALSE;

-- For existing users already in the system, mark them as verified

UPDATE users SET is_verified = TRUE WHERE is_verified = FALSE;


SELECT id, name, email, is_verified, is_active FROM users LIMIT 10;