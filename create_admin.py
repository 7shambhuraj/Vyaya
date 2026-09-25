
from werkzeug.security import generate_password_hash
import psycopg2

DB_CONFIG = {
    'host': 'localhost',
    'database': 'expense_tracker_db',
    'user': 'postgres',
    'password': 'SHAMBHU11',  
    'port': '5432'
}

def create_admin(name, email, password, role='superadmin'):
    conn = psycopg2.connect(**DB_CONFIG)
    cur  = conn.cursor()
    hashed = generate_password_hash(password)
    cur.execute(
        "INSERT INTO admins (name, email, password_hash, role) VALUES (%s,%s,%s,%s) ON CONFLICT (email) DO UPDATE SET password_hash=%s, role=%s",
        (name, email, hashed, role, hashed, role)
    )
    conn.commit(); cur.close(); conn.close()
    print(f"✅ Admin account created!")
    print(f"   Email : {email}")
    print(f"   Pass  : {password}")
    print(f"   Role  : {role}")
    print(f"\n   Login at: http://localhost:5000/admin/login")

if __name__ == '__main__':
    print("=" * 45)
    print("  SpendWise — Create Admin Account")
    print("=" * 45)
    name     = input("Admin name    : ").strip() or "Super Admin"
    email    = input("Admin email   : ").strip() or "admin@spendwise.com"
    password = input("Admin password: ").strip() or "admin123"
    create_admin(name, email, password)
