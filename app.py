from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_mail import Mail, Message
from itsdangerous import URLSafeTimedSerializer, SignatureExpired, BadSignature
import psycopg2
import psycopg2.extras
import os
from datetime import datetime, date
from functools import wraps

app = Flask(__name__)
app.secret_key = 'expense_tracker_secret_key_2024'

# ── File Upload ───────────────────────────────────────────────
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

# ── Email Config (Gmail SMTP) ─────────────────────────────────
# STEP 1: Enable 2-Step Verification on your Gmail account
# STEP 2: Go to Google Account → Security → App Passwords
# STEP 3: Generate an App Password for "Mail" → copy the 16-char code
# STEP 4: Paste it below as MAIL_PASSWORD
app.config['MAIL_SERVER']   = 'smtp.gmail.com'
app.config['MAIL_PORT']     = 587
app.config['MAIL_USE_TLS']  = True
app.config['MAIL_USERNAME'] = '7shambhuraj@gmail.com'      #   Gmail
app.config['MAIL_PASSWORD'] = 'adbv idgj cdqn hoqq'    # ← 16-char App Password
app.config['MAIL_DEFAULT_SENDER'] = ('Vyaya ET', '7shambhuraj@gmail.com')

mail = Mail(app)
serializer = URLSafeTimedSerializer(app.secret_key)

# ── Database ──────────────────────────────────────────────────
DB_CONFIG = {
    'host': 'localhost',
    'database': 'expense_tracker_db',
    'user': 'postgres',
    'password': 'SHAMBHU11',   
    'port': '5432'
}

MEMBERSHIP_RANKS = {
    'Free':       {'color': '#6b7280', 'icon': 'fa-circle',    'order': 1, 'badge': '#374151'},
    'Silver':     {'color': '#94a3b8', 'icon': 'fa-medal',     'order': 2, 'badge': '#1e293b'},
    'Gold':       {'color': '#f59e0b', 'icon': 'fa-crown',     'order': 3, 'badge': '#451a03'},
    'Platinum':   {'color': '#38bdf8', 'icon': 'fa-gem',       'order': 4, 'badge': '#0c1a2e'},
    'Diamond':    {'color': '#a78bfa', 'icon': 'fa-diamond',   'order': 5, 'badge': '#2e1065'},
    'Enterprise': {'color': '#ff6b6b', 'icon': 'fa-building',  'order': 6, 'badge': '#3b0000'},
}

def get_db():
    return psycopg2.connect(**DB_CONFIG)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# ── Email helpers ─────────────────────────────────────────────
def send_verification_email(user_email, user_name):
    token = serializer.dumps(user_email, salt='email-verify')
    verify_url = url_for('verify_email', token=token, _external=True)
    msg = Message(
        subject='✅ Verify your Vyaya ET account',
        recipients=[user_email]
    )
    msg.html = f"""
    <div style="font-family:Arial,sans-serif;max-width:520px;margin:0 auto;background:#0d0f1a;color:#eef0f8;padding:32px;border-radius:12px;">
      <div style="text-align:center;margin-bottom:28px;">
        <h1 style="color:#4f8ef7;font-size:28px;margin:0;">🧾 Vyaya ET</h1>
        <p style="color:#8b92b8;margin:6px 0 0;">Personal Expense Tracker</p>
      </div>
      <h2 style="color:#eef0f8;font-size:20px;">Hi {user_name},</h2>
      <p style="color:#8b92b8;line-height:1.7;">
        Thank you for registering with <strong style="color:#4f8ef7;">Vyaya ET</strong>!
        Please click the button below to verify your email address and activate your account.
      </p>
      <div style="text-align:center;margin:32px 0;">
        <a href="{verify_url}"
           style="background:linear-gradient(135deg,#4f8ef7,#6b5cf6);color:#fff;
                  padding:14px 36px;border-radius:8px;text-decoration:none;
                  font-weight:bold;font-size:16px;display:inline-block;">
          ✅ Verify Email Address
        </a>
      </div>
      <p style="color:#555e85;font-size:13px;text-align:center;">
        This link expires in <strong>1 hour</strong>. If you did not register, ignore this email.
      </p>
      <hr style="border:none;border-top:1px solid #1e2440;margin:24px 0;">
      <p style="color:#555e85;font-size:12px;text-align:center;">
        © 2025 Vyaya ET · Personal Expense Tracker
      </p>
    </div>
    """
    mail.send(msg)

def send_welcome_email(user_email, user_name):
    msg = Message(
        subject='🎉 Welcome to Vyaya ET!',
        recipients=[user_email]
    )
    msg.html = f"""
    <div style="font-family:Arial,sans-serif;max-width:520px;margin:0 auto;background:#0d0f1a;color:#eef0f8;padding:32px;border-radius:12px;">
      <div style="text-align:center;margin-bottom:28px;">
        <h1 style="color:#4f8ef7;font-size:28px;margin:0;">💳 Vyaya ET</h1>
      </div>
      <h2 style="color:#36d399;font-size:22px;">🎉 Your account is verified!</h2>
      <p style="color:#8b92b8;line-height:1.7;">
        Hi <strong style="color:#eef0f8;">{user_name}</strong>, your Vyaya ET account is now active.
        You can log in and start tracking your expenses!
      </p>
      <div style="text-align:center;margin:28px 0;">
        <a href="{url_for('login', _external=True)}"
           style="background:linear-gradient(135deg,#36d399,#059669);color:#fff;
                  padding:12px 32px;border-radius:8px;text-decoration:none;
                  font-weight:bold;font-size:15px;display:inline-block;">
          Login Now →
        </a>
      </div>
      <hr style="border:none;border-top:1px solid #1e2440;margin:20px 0;">
      <p style="color:#555e85;font-size:12px;text-align:center;">© 2025 Vyaya ET</p>
    </div>
    """
    mail.send(msg)

# ── Decorators ────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'admin_id' not in session:
            flash('Admin access required.', 'error')
            return redirect(url_for('admin_login'))
        return f(*args, **kwargs)
    return decorated

# ═══════════════════════════════════════
#  USER ROUTES
# ═══════════════════════════════════════
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name        = request.form.get('name','').strip()
        email       = request.form.get('email','').strip()
        password    = request.form.get('password','')
        phone       = request.form.get('phone','').strip()
        profile_pic = None

        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"{datetime.now().timestamp()}_{file.filename}")
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                profile_pic = filename
        try:
            conn = get_db(); cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE email=%s", (email,))
            if cur.fetchone():
                flash('Email already registered.', 'error')
                return redirect(url_for('register'))

            # Insert user with is_verified = FALSE
            cur.execute(
                """INSERT INTO users
                   (name,email,password_hash,phone,profile_picture,membership,is_verified)
                   VALUES (%s,%s,%s,%s,%s,'Free',FALSE)""",
                (name, email, generate_password_hash(password), phone, profile_pic)
            )
            conn.commit(); cur.close(); conn.close()

            # Send verification email
            try:
                send_verification_email(email, name)
                flash('✅ Registration successful! Please check your email to verify your account.', 'success')
            except Exception as mail_err:
                flash(f'Account created but email failed: {str(mail_err)}. Contact admin.', 'warning')

            return redirect(url_for('login'))
        except Exception as e:
            flash(f'Registration failed: {str(e)}', 'error')
    return render_template('register.html')

@app.route('/verify/<token>')
def verify_email(token):
    try:
        email = serializer.loads(token, salt='email-verify', max_age=3600)  # 1 hour
    except SignatureExpired:
        flash('⏰ Verification link has expired. Please register again or request a new link.', 'error')
        return redirect(url_for('login'))
    except BadSignature:
        flash('❌ Invalid verification link.', 'error')
        return redirect(url_for('login'))

    try:
        conn = get_db()
        cur  = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM users WHERE email=%s", (email,))
        user = cur.fetchone()

        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('login'))

        if user['is_verified']:
            flash('✅ Email already verified. Please login.', 'info')
            return redirect(url_for('login'))

        cur.execute("UPDATE users SET is_verified=TRUE, is_active=TRUE WHERE email=%s", (email,))
        conn.commit(); cur.close(); conn.close()

        # Send welcome email
        try:
            send_welcome_email(email, user['name'])
        except: pass

        flash(f'🎉 Email verified successfully! Welcome, {user["name"]}! You can now login.', 'success')
        return redirect(url_for('login'))
    except Exception as e:
        flash(f'Verification error: {str(e)}', 'error')
        return redirect(url_for('login'))

@app.route('/resend_verification', methods=['GET', 'POST'])
def resend_verification():
    if request.method == 'POST':
        email = request.form.get('email','').strip()
        try:
            conn = get_db()
            cur  = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cur.fetchone(); cur.close(); conn.close()

            if not user:
                flash('No account found with that email.', 'error')
            elif user['is_verified']:
                flash('This email is already verified. Please login.', 'info')
                return redirect(url_for('login'))
            else:
                send_verification_email(email, user['name'])
                flash('✅ Verification email resent! Please check your inbox.', 'success')
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
    return render_template('resend_verification.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form.get('email','').strip()
        password = request.form.get('password','')
        try:
            conn = get_db()
            cur  = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("SELECT * FROM users WHERE email=%s", (email,))
            user = cur.fetchone(); cur.close(); conn.close()

            if user and check_password_hash(user['password_hash'], password):
                if not user['is_active']:
                    flash('Your account has been deactivated. Contact admin.', 'error')
                    return redirect(url_for('login'))
                # Check email verification
                if not user['is_verified']:
                    flash('⚠️ Please verify your email before logging in. '
                          '<a href="/resend_verification" style="color:#4f8ef7;">Resend verification email</a>', 'warning')
                    return redirect(url_for('login'))
                session['user_id']         = user['id']
                session['user_name']       = user['name']
                session['user_pic']        = user['profile_picture']
                session['user_membership'] = user['membership'] or 'Free'
                flash(f'Welcome back, {user["name"]}!', 'success')
                return redirect(url_for('dashboard'))
            flash('Invalid email or password.', 'error')
        except Exception as e:
            flash(f'Login failed: {str(e)}', 'error')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        conn = get_db()
        cur  = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        uid  = session['user_id']
        cur.execute("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE user_id=%s AND EXTRACT(MONTH FROM expense_date)=EXTRACT(MONTH FROM CURRENT_DATE) AND EXTRACT(YEAR FROM expense_date)=EXTRACT(YEAR FROM CURRENT_DATE)", (uid,))
        monthly_total = float(cur.fetchone()[0])
        cur.execute("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE user_id=%s AND expense_date=CURRENT_DATE", (uid,))
        today_total = float(cur.fetchone()[0])
        cur.execute("SELECT COUNT(*) FROM expenses WHERE user_id=%s", (uid,))
        total_transactions = cur.fetchone()[0]
        cur.execute("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE user_id=%s AND EXTRACT(YEAR FROM expense_date)=EXTRACT(YEAR FROM CURRENT_DATE)", (uid,))
        yearly_total = float(cur.fetchone()[0])
        cur.execute("SELECT * FROM expenses WHERE user_id=%s ORDER BY created_at DESC LIMIT 10", (uid,))
        recent_expenses = cur.fetchall()
        cur.execute("SELECT category, COALESCE(SUM(amount),0) as total FROM expenses WHERE user_id=%s AND EXTRACT(MONTH FROM expense_date)=EXTRACT(MONTH FROM CURRENT_DATE) GROUP BY category ORDER BY total DESC", (uid,))
        category_data = cur.fetchall()
        cur.execute("SELECT TO_CHAR(expense_date,'Mon') as month, EXTRACT(MONTH FROM expense_date) as month_num, COALESCE(SUM(amount),0) as total FROM expenses WHERE user_id=%s AND expense_date >= CURRENT_DATE - INTERVAL '6 months' GROUP BY TO_CHAR(expense_date,'Mon'), EXTRACT(MONTH FROM expense_date) ORDER BY month_num", (uid,))
        monthly_trend = cur.fetchall()
        cur.execute("SELECT membership FROM users WHERE id=%s", (uid,))
        row = cur.fetchone()
        if row: session['user_membership'] = row['membership'] or 'Free'
        cur.close(); conn.close()
        membership_info = MEMBERSHIP_RANKS.get(session.get('user_membership','Free'), MEMBERSHIP_RANKS['Free'])
        return render_template('dashboard.html',
            monthly_total=monthly_total, today_total=today_total,
            total_transactions=total_transactions, yearly_total=yearly_total,
            recent_expenses=recent_expenses, category_data=category_data,
            monthly_trend=monthly_trend, today=str(date.today()), now=datetime.now(),
            membership_info=membership_info, membership_ranks=MEMBERSHIP_RANKS
        )
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return render_template('dashboard.html',
            monthly_total=0, today_total=0, total_transactions=0, yearly_total=0,
            recent_expenses=[], category_data=[], monthly_trend=[],
            today=str(date.today()), now=datetime.now(),
            membership_info=MEMBERSHIP_RANKS['Free'], membership_ranks=MEMBERSHIP_RANKS
        )

@app.route('/add_expense', methods=['POST'])
@login_required
def add_expense():
    try:
        conn = get_db(); cur = conn.cursor()
        cur.execute("INSERT INTO expenses (user_id,title,amount,category,expense_date,description) VALUES (%s,%s,%s,%s,%s,%s)",
            (session['user_id'], request.form.get('title','').strip(),
             float(request.form.get('amount',0)), request.form.get('category','Other'),
             request.form.get('expense_date', str(date.today())),
             request.form.get('description','').strip()))
        conn.commit(); cur.close(); conn.close()
        flash('Expense added!', 'success')
    except Exception as e:
        flash(f'Failed: {str(e)}', 'error')
    return redirect(url_for('dashboard'))

@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    try:
        conn = get_db(); cur = conn.cursor()
        cur.execute("DELETE FROM expenses WHERE id=%s AND user_id=%s", (expense_id, session['user_id']))
        conn.commit(); cur.close(); conn.close()
        flash('Deleted.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('dashboard'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    conn = get_db()
    cur  = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM users WHERE id=%s", (session['user_id'],))
    user = cur.fetchone()
    if request.method == 'POST':
        name  = request.form.get('name','').strip()
        phone = request.form.get('phone','').strip()
        pic   = user['profile_picture']
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(f"{datetime.now().timestamp()}_{file.filename}")
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                pic = filename
        cur.execute("UPDATE users SET name=%s, phone=%s, profile_picture=%s WHERE id=%s",
                    (name, phone, pic, session['user_id']))
        conn.commit()
        session['user_name'] = name; session['user_pic'] = pic
        flash('Profile updated!', 'success')
        return redirect(url_for('profile'))
    cur.close(); conn.close()
    membership_info = MEMBERSHIP_RANKS.get(user['membership'] or 'Free', MEMBERSHIP_RANKS['Free'])
    return render_template('profile.html', user=user,
                           membership_info=membership_info, membership_ranks=MEMBERSHIP_RANKS)

# ═══════════════════════════════════════
#  ABOUT & SUPPORT
# ═══════════════════════════════════════
@app.route('/about', methods=['GET', 'POST'])
def about():
    if request.method == 'POST':
        name    = request.form.get('name','').strip()
        email   = request.form.get('email','').strip()
        subject = request.form.get('subject','').strip()
        message = request.form.get('message','').strip()
        user_id = session.get('user_id', None)
        if not name or not email or not message:
            flash('Please fill in all required fields.', 'error')
            return redirect(url_for('about') + '#contact')
        try:
            conn = get_db(); cur = conn.cursor()
            cur.execute(
                "INSERT INTO support_messages (user_id,name,email,subject,message) VALUES (%s,%s,%s,%s,%s)",
                (user_id, name, email, subject, message)
            )
            conn.commit(); cur.close(); conn.close()
            flash('Your message has been sent!', 'success')
        except Exception as e:
            flash(f'Failed: {str(e)}', 'error')
        return redirect(url_for('about') + '#contact')
    return render_template('about.html')

# ═══════════════════════════════════════
#  ADMIN ROUTES
# ═══════════════════════════════════════
@app.route('/admin')
def admin_index():
    return redirect(url_for('admin_dashboard') if 'admin_id' in session else url_for('admin_login'))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if 'admin_id' in session:
        return redirect(url_for('admin_dashboard'))
    if request.method == 'POST':
        email    = request.form.get('email','').strip()
        password = request.form.get('password','')
        try:
            conn = get_db()
            cur  = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute("SELECT * FROM admins WHERE email=%s", (email,))
            admin = cur.fetchone(); cur.close(); conn.close()
            if admin and check_password_hash(admin['password_hash'], password):
                session['admin_id']   = admin['id']
                session['admin_name'] = admin['name']
                session['admin_role'] = admin['role']
                flash(f'Welcome, {admin["name"]}!', 'success')
                return redirect(url_for('admin_dashboard'))
            flash('Invalid admin credentials.', 'error')
        except Exception as e:
            flash(f'Login error: {str(e)}', 'error')
    return render_template('admin/admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    for k in ('admin_id','admin_name','admin_role'): session.pop(k, None)
    flash('Admin logged out.', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    try:
        conn = get_db()
        cur  = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT COUNT(*) FROM users"); total_users = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM expenses"); total_expenses = cur.fetchone()[0]
        cur.execute("SELECT COALESCE(SUM(amount),0) FROM expenses"); platform_total = float(cur.fetchone()[0])
        cur.execute("SELECT COUNT(*) FROM users WHERE created_at >= CURRENT_DATE - INTERVAL '7 days'"); new_this_week = cur.fetchone()[0]
        cur.execute("SELECT membership, COUNT(*) as cnt FROM users GROUP BY membership ORDER BY cnt DESC")
        membership_stats = cur.fetchall()
        cur.execute("""
            SELECT u.id, u.name, u.email, u.phone, u.profile_picture,
                   u.membership, u.created_at, u.is_active, u.is_verified,
                   COUNT(e.id) as expense_count,
                   COALESCE(SUM(e.amount),0) as total_spent
            FROM users u LEFT JOIN expenses e ON e.user_id=u.id
            GROUP BY u.id ORDER BY u.created_at DESC
        """)
        users = cur.fetchall()
        cur.execute("""
            SELECT e.title, e.amount, e.category, e.expense_date, u.name as user_name
            FROM expenses e JOIN users u ON u.id=e.user_id
            ORDER BY e.created_at DESC LIMIT 8
        """)
        recent_activity = cur.fetchall()
        cur.close(); conn.close()
        return render_template('admin/admin_dashboard.html',
            total_users=total_users, total_expenses=total_expenses,
            platform_total=platform_total, new_this_week=new_this_week,
            membership_stats=membership_stats, users=users,
            recent_activity=recent_activity, membership_ranks=MEMBERSHIP_RANKS
        )
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return render_template('admin/admin_dashboard.html',
            total_users=0, total_expenses=0, platform_total=0,
            new_this_week=0, membership_stats=[], users=[],
            recent_activity=[], membership_ranks=MEMBERSHIP_RANKS
        )

@app.route('/admin/user/<int:user_id>')
@admin_required
def admin_user_detail(user_id):
    try:
        conn = get_db()
        cur  = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM users WHERE id=%s", (user_id,))
        user = cur.fetchone()
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('admin_dashboard'))
        cur.execute("SELECT * FROM expenses WHERE user_id=%s ORDER BY expense_date DESC", (user_id,))
        expenses = cur.fetchall()
        cur.execute("SELECT COALESCE(SUM(amount),0) FROM expenses WHERE user_id=%s", (user_id,))
        total_spent = float(cur.fetchone()[0])
        cur.execute("SELECT category, COALESCE(SUM(amount),0) as total FROM expenses WHERE user_id=%s GROUP BY category ORDER BY total DESC", (user_id,))
        cat_breakdown = cur.fetchall()
        cur.close(); conn.close()
        membership_info = MEMBERSHIP_RANKS.get(user['membership'] or 'Free', MEMBERSHIP_RANKS['Free'])
        return render_template('admin/admin_user_detail.html',
            user=user, expenses=expenses, total_spent=total_spent,
            cat_breakdown=cat_breakdown, membership_info=membership_info,
            membership_ranks=MEMBERSHIP_RANKS
        )
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/update_membership', methods=['POST'])
@admin_required
def admin_update_membership():
    user_id    = request.form.get('user_id')
    membership = request.form.get('membership')
    if membership not in MEMBERSHIP_RANKS:
        flash('Invalid rank.', 'error')
        return redirect(url_for('admin_dashboard'))
    try:
        conn = get_db(); cur = conn.cursor()
        cur.execute("UPDATE users SET membership=%s WHERE id=%s", (membership, user_id))
        conn.commit()
        cur2 = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur2.execute("SELECT name FROM users WHERE id=%s", (user_id,))
        row = cur2.fetchone()
        cur.close(); cur2.close(); conn.close()
        flash(f'✅ {row["name"] if row else "User"} assigned {membership} rank!', 'success')
    except Exception as e:
        flash(f'Update failed: {str(e)}', 'error')
    redirect_to = request.form.get('redirect_to','admin_dashboard')
    if redirect_to == 'user_detail':
        return redirect(url_for('admin_user_detail', user_id=user_id))
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/toggle_user/<int:user_id>', methods=['POST'])
@admin_required
def admin_toggle_user(user_id):
    try:
        conn = get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT is_active, name FROM users WHERE id=%s", (user_id,))
        row = cur.fetchone()
        if row:
            cur.execute("UPDATE users SET is_active=%s WHERE id=%s", (not row['is_active'], user_id))
            conn.commit()
            flash(f'{row["name"]} {"activated" if not row["is_active"] else "deactivated"}.', 'success')
        cur.close(); conn.close()
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    try:
        conn = get_db(); cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE id=%s", (user_id,))
        conn.commit(); cur.close(); conn.close()
        flash('User deleted.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/messages')
@admin_required
def admin_messages():
    try:
        conn = get_db()
        cur  = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT * FROM support_messages ORDER BY created_at DESC")
        messages = cur.fetchall()
        cur.execute("SELECT COUNT(*) FROM support_messages WHERE is_read = FALSE")
        unread_count = cur.fetchone()[0]
        cur.close(); conn.close()
        return render_template('admin/admin_messages.html',
                               messages=messages, unread_count=unread_count)
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return render_template('admin/admin_messages.html', messages=[], unread_count=0)

@app.route('/admin/messages/read/<int:msg_id>', methods=['POST'])
@admin_required
def admin_mark_read(msg_id):
    try:
        conn = get_db(); cur = conn.cursor()
        cur.execute("UPDATE support_messages SET is_read=TRUE WHERE id=%s", (msg_id,))
        conn.commit(); cur.close(); conn.close()
    except: pass
    return redirect(url_for('admin_messages'))

@app.route('/admin/messages/delete/<int:msg_id>', methods=['POST'])
@admin_required
def admin_delete_message(msg_id):
    try:
        conn = get_db(); cur = conn.cursor()
        cur.execute("DELETE FROM support_messages WHERE id=%s", (msg_id,))
        conn.commit(); cur.close(); conn.close()
        flash('Message deleted.', 'success')
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
    return redirect(url_for('admin_messages'))

@app.route('/admin/api/stats')
@admin_required
def admin_api_stats():
    try:
        conn = get_db(); cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute("SELECT membership, COUNT(*) as cnt FROM users GROUP BY membership")
        ranks = cur.fetchall()
        cur.execute("""
            SELECT TO_CHAR(created_at,'Mon') as month, COUNT(*) as cnt
            FROM users WHERE created_at >= CURRENT_DATE - INTERVAL '6 months'
            GROUP BY TO_CHAR(created_at,'Mon'), EXTRACT(MONTH FROM created_at)
            ORDER BY EXTRACT(MONTH FROM created_at)
        """)
        growth = cur.fetchall(); cur.close(); conn.close()
        return jsonify({
            'ranks':  [{'name': r['membership'], 'count': r['cnt']} for r in ranks],
            'growth': [{'month': r['month'], 'count': r['cnt']} for r in growth]
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500



# ═══════════════════════════════════════
#  BUDGET ROUTES
# ═══════════════════════════════════════

@app.route('/budgets')
@login_required
def budgets():
    try:
        conn = get_db()
        cur  = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        uid  = session['user_id']
        now  = datetime.now()

        cur.execute("""
            SELECT b.*,
                CASE
                    WHEN b.budget_type='monthly' THEN (
                        SELECT COALESCE(SUM(e.amount),0)
                        FROM expenses e
                        WHERE e.user_id=b.user_id
                          AND EXTRACT(MONTH FROM e.expense_date)=b.month
                          AND EXTRACT(YEAR  FROM e.expense_date)=b.year
                          AND (b.category='Overall' OR e.category=b.category)
                    )
                    ELSE (
                        SELECT COALESCE(SUM(e.amount),0)
                        FROM expenses e
                        WHERE e.user_id=b.user_id
                          AND EXTRACT(YEAR FROM e.expense_date)=b.year
                          AND (b.category='Overall' OR e.category=b.category)
                    )
                END AS spent
            FROM budgets b
            WHERE b.user_id=%s
            ORDER BY b.year DESC, b.month DESC NULLS LAST, b.budget_type
        """, (uid,))
        all_budgets = cur.fetchall()

        cur.execute("""
            SELECT b.*, 
                (SELECT COALESCE(SUM(e.amount),0) FROM expenses e
                 WHERE e.user_id=b.user_id
                   AND EXTRACT(MONTH FROM e.expense_date)=%s
                   AND EXTRACT(YEAR  FROM e.expense_date)=%s
                   AND (b.category='Overall' OR e.category=b.category)
                ) AS spent
            FROM budgets b
            WHERE b.user_id=%s AND b.budget_type='monthly'
              AND b.month=%s AND b.year=%s
        """, (now.month, now.year, uid, now.month, now.year))
        monthly_budgets = cur.fetchall()

        cur.execute("""
            SELECT b.*,
                (SELECT COALESCE(SUM(e.amount),0) FROM expenses e
                 WHERE e.user_id=b.user_id
                   AND EXTRACT(YEAR FROM e.expense_date)=%s
                   AND (b.category='Overall' OR e.category=b.category)
                ) AS spent
            FROM budgets b
            WHERE b.user_id=%s AND b.budget_type='yearly' AND b.year=%s
        """, (now.year, uid, now.year))
        yearly_budgets = cur.fetchall()

        cur.execute("""
            SELECT category, COALESCE(SUM(amount),0) as spent
            FROM expenses
            WHERE user_id=%s
              AND EXTRACT(MONTH FROM expense_date)=%s
              AND EXTRACT(YEAR  FROM expense_date)=%s
            GROUP BY category ORDER BY spent DESC
        """, (uid, now.month, now.year))
        cat_spending = cur.fetchall()

        cur.close(); conn.close()

        return render_template('budgets.html',
            all_budgets=all_budgets,
            monthly_budgets=monthly_budgets,
            yearly_budgets=yearly_budgets,
            cat_spending=cat_spending,
            now=now,
            membership_ranks=MEMBERSHIP_RANKS
        )

    except Exception as e:
        flash(f'Error loading budgets: {str(e)}', 'error')
        return render_template('budgets.html',
            all_budgets=[], monthly_budgets=[], yearly_budgets=[],
            cat_spending=[], now=datetime.now(),
            membership_ranks=MEMBERSHIP_RANKS
        )


@app.route('/budgets/add', methods=['POST'])
@login_required
def add_budget():
    try:
        uid         = session['user_id']
        budget_type = request.form.get('budget_type', 'monthly')
        amount      = float(request.form.get('amount', 0))
        year        = int(request.form.get('year', datetime.now().year))
        month       = int(request.form.get('month', datetime.now().month)) if budget_type == 'monthly' else None
        category    = request.form.get('category', 'Overall')
        note        = request.form.get('note', '').strip()

        conn = get_db(); cur = conn.cursor()
        cur.execute("""
            INSERT INTO budgets (user_id, budget_type, amount, year, month, category, note)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            ON CONFLICT (user_id, budget_type, year, month, category)
            DO UPDATE SET amount=%s, note=%s
        """, (uid, budget_type, amount, year, month, category, note, amount, note))

        conn.commit(); cur.close(); conn.close()
        flash('✅ Budget saved successfully!', 'success')

    except Exception as e:
        flash(f'Failed to save budget: {str(e)}', 'error')

    return redirect(url_for('budgets'))


@app.route('/budgets/delete/<int:budget_id>', methods=['POST'])
@login_required
def delete_budget(budget_id):
    try:
        conn = get_db(); cur = conn.cursor()
        cur.execute(
            "DELETE FROM budgets WHERE id=%s AND user_id=%s",
            (budget_id, session['user_id'])
        )
        conn.commit(); cur.close(); conn.close()
        flash('Budget deleted.', 'success')

    except Exception as e:
        flash(f'Error: {str(e)}', 'error')

    return redirect(url_for('budgets'))


# ✅ ALWAYS KEEP THIS LAST
if __name__ == '__main__':
    app.run(debug=True, port=5000)

print(app.url_map)


if __name__ == '__main__':
    app.run(debug=True, port=5000)