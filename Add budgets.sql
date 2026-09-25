CREATE TABLE IF NOT EXISTS budgets (
    id          SERIAL        PRIMARY KEY,
    user_id     INTEGER       NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    budget_type VARCHAR(10)   NOT NULL CHECK (budget_type IN ('monthly','yearly')),
    amount      DECIMAL(12,2) NOT NULL CHECK (amount > 0),
    month       INTEGER       CHECK (month BETWEEN 1 AND 12),
    year        INTEGER       NOT NULL,
    category    VARCHAR(50)   DEFAULT 'Overall',
    note        TEXT,
    created_at  TIMESTAMP     NOT NULL DEFAULT CURRENT_TIMESTAMP,
   
    UNIQUE (user_id, budget_type, year, month, category)
);

CREATE INDEX IF NOT EXISTS idx_budgets_user_id ON budgets(user_id);
CREATE INDEX IF NOT EXISTS idx_budgets_year    ON budgets(year);
CREATE INDEX IF NOT EXISTS idx_budgets_type    ON budgets(budget_type);


SELECT 'budgets table ready!' AS status;