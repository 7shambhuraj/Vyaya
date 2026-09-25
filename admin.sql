INSERT INTO admins (name, email, password_hash, role)
VALUES (
    'Super Admin',
    'admin@spendwise.com',
    'PASTE_THE_HASH_HERE',
    'superadmin'
)
ON CONFLICT (email) DO NOTHING;