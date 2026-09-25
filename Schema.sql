
DROP TABLE IF EXISTS expenses CASCADE;
DROP TABLE IF EXISTS users    CASCADE;
DROP TABLE IF EXISTS admins   CASCADE;



CREATE TABLE users (
    id               SERIAL        PRIMARY KEY,
    name             VARCHAR(100)  NOT NULL,
    email            VARCHAR(150)  UNIQUE NOT NULL,
    password_hash    TEXT          NOT NULL,
    phone            VARCHAR(20),
    profile_picture  VARCHAR(255),
    membership       VARCHAR(20)   NOT NULL DEFAULT 'Free',
    is_active        BOOLEAN       NOT NULL DEFAULT TRUE,
    created_at       TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE admins (
    id            SERIAL        PRIMARY KEY,
    name          VARCHAR(100)  NOT NULL,
    email         VARCHAR(150)  UNIQUE NOT NULL,
    password_hash TEXT          NOT NULL,
    role          VARCHAR(30)   NOT NULL DEFAULT 'admin',
    created_at    TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE expenses (
    id           SERIAL         PRIMARY KEY,
    user_id      INTEGER        NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    title        VARCHAR(200)   NOT NULL,
    amount       DECIMAL(12,2)  NOT NULL CHECK (amount >= 0),
    category     VARCHAR(50)    NOT NULL DEFAULT 'Other',
    expense_date DATE           NOT NULL DEFAULT CURRENT_DATE,
    description  TEXT,
    created_at   TIMESTAMP      NOT NULL DEFAULT CURRENT_TIMESTAMP
);



CREATE INDEX idx_expenses_user_id  ON expenses(user_id);
CREATE INDEX idx_expenses_date     ON expenses(expense_date);
CREATE INDEX idx_expenses_category ON expenses(category);
CREATE INDEX idx_users_membership  ON users(membership);
CREATE INDEX idx_users_email       ON users(email);
CREATE INDEX idx_admins_email      ON admins(email);



INSERT INTO users (name, email, password_hash, phone, membership, is_active) VALUES
('Rahul S',  'rahul@gmail.com',  '123456', '9876543210', 'Gold',       TRUE),
('Priya Patil',   'priya@gmial.com',  'placeholder_hash', '9988776655', 'Silver',     TRUE),
('Amit Desai',    'amit@gmail.com',   'a122', '9123456789', 'Platinum',   TRUE),
('Neha Kulkarni', 'neha@gmail.com',   'placeholder_hash', '9001234567', 'Free',       TRUE),
('Vikram S',  'vikram@gmail.com', '123456', '9555123456', 'Diamond',    TRUE),
('Sneha Joshi',   'sneha@gmail.com',  'placeholder_hash', '9444987654', 'Enterprise', TRUE);



INSERT INTO expenses (user_id, title, amount, category, expense_date, description) VALUES
(1, 'Weekly Groceries',       2500.00, 'Food/bhaji pala',          CURRENT_DATE,        'Big bazaar shopping'),
(1, 'Electricity Bill',       1800.00, 'Utilities',     CURRENT_DATE - 2,    'Monthly electricity bill'),
(1, 'Netflix Subscription',    649.00, 'Entertainment', CURRENT_DATE - 5,    'Monthly streaming'),
(1, 'Petrol Fill-up',         3000.00, 'Transport',     CURRENT_DATE - 7,    'Full tank petrol'),
(1, 'Doctor Visit',            800.00, 'Healthcare',    CURRENT_DATE - 10,   'General checkup'),
(1, 'Online Python Course',   1999.00, 'Education',     CURRENT_DATE - 15,   'Udemy course'),
(1, 'Restaurant Dinner',      1200.00, 'Food',          CURRENT_DATE - 20,   'Dinner with friends'),
(1, 'Gym Membership',         2000.00, 'Health',        CURRENT_DATE - 25,   'Monthly gym fee'),
(1, 'Uber Ride',               450.00, 'Transport',     CURRENT_DATE - 3,    'Office commute'),
(1, 'Amazon Shopping',        3500.00, 'Shopping',      CURRENT_DATE - 8,    'New headphones'),
(1, 'Water Bill',              350.00, 'Utilities',     CURRENT_DATE - 12,   'Monthly water'),
(1, 'Movie Tickets',           800.00, 'Entertainment', CURRENT_DATE - 18,   '2 tickets plus popcorn'),
(2, 'Grocery Shopping',       1800.00, 'Food',          CURRENT_DATE - 1,    'D-mart weekly'),
(2, 'Internet Bill',           999.00, 'Utilities',     CURRENT_DATE - 4,    'Broadband monthly'),
(2, 'Zomato Order',            450.00, 'Food',          CURRENT_DATE - 6,    'Lunch delivery'),
(2, 'Auto Rickshaw',           120.00, 'Transport',     CURRENT_DATE - 9,    'Local travel'),
(2, 'Medicine',                650.00, 'Healthcare',    CURRENT_DATE - 14,   'Monthly medicines'),
(2, 'Books',                   850.00, 'Education',     CURRENT_DATE - 22,   'Study material'),
(3, 'Flight Tickets',        12000.00, 'Travel',        CURRENT_DATE - 3,    'Mumbai to Delhi'),
(3, 'Hotel Stay',             8500.00, 'Travel',        CURRENT_DATE - 5,    '2 nights hotel'),
(3, 'Business Lunch',         2200.00, 'Food',          CURRENT_DATE - 7,    'Client meeting'),
(3, 'Laptop Accessory',       4500.00, 'Shopping',      CURRENT_DATE - 11,   'USB hub and mouse'),
(3, 'Mobile Recharge',         699.00, 'Utilities',     CURRENT_DATE - 16,   'Monthly plan'),
(4, 'Vegetable Market',        600.00, 'Food',          CURRENT_DATE - 2,    'Weekly vegetables'),
(4, 'Bus Pass',                500.00, 'Transport',     CURRENT_DATE - 30,   'Monthly bus pass'),
(4, 'Tuition Fee',            3000.00, 'Education',     CURRENT_DATE - 10,   'Online class'),
(5, 'Car Service',            5500.00, 'Transport',     CURRENT_DATE - 4,    'Annual car service'),
(5, 'Protein Supplements',    2800.00, 'Health',        CURRENT_DATE - 8,    'Whey protein tub'),
(5, 'Sports Equipment',       4200.00, 'Health',        CURRENT_DATE - 15,   'Badminton racket'),
(5, 'OTT Bundle',              999.00, 'Entertainment', CURRENT_DATE - 20,   'Hotstar plus Prime'),
(6, 'Office Supplies',        1500.00, 'Shopping',      CURRENT_DATE - 3,    'Stationery'),
(6, 'Team Lunch',             3200.00, 'Food',          CURRENT_DATE - 6,    'Monthly team outing'),
(6, 'Conference Ticket',      5000.00, 'Education',     CURRENT_DATE - 12,   'Tech conference'),
(6, 'Cab to Airport',         1200.00, 'Transport',     CURRENT_DATE - 18,   'Business trip');



INSERT INTO admins (name, email, password_hash, role) VALUES
('Super Admin', 'admin@spendwise.com', 'PASTE_YOUR_HASH_HERE', 'superadmin')
ON CONFLICT (email) DO NOTHING;



SELECT 'users'    AS table_name, COUNT(*) AS total_rows FROM users
UNION ALL
SELECT 'admins',                  COUNT(*)               FROM admins
UNION ALL
SELECT 'expenses',                COUNT(*)               FROM expenses;