-- Schema für investment-transaction-analyzer
-- Eine zentrale Tabelle: transactions
-- CHECK-Constraints stellen sicher, dass nur erlaubte Werte landen.

CREATE TABLE IF NOT EXISTS transactions (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    date             DATE    NOT NULL,
    transaction_type TEXT    NOT NULL CHECK (transaction_type IN (
        'buy', 'sell', 'dividend', 'deposit', 'withdrawal', 'fee', 'tax'
    )),
    asset_class      TEXT    NOT NULL CHECK (asset_class IN (
        'stock', 'etf', 'crypto', 'precious_metal',
        'private_equity', 'cash', 'other'
    )),
    asset_name       TEXT    NOT NULL,
    ticker           TEXT,
    broker           TEXT,
    currency         TEXT    NOT NULL,
    quantity         REAL    NOT NULL DEFAULT 0,
    price_per_unit   REAL    NOT NULL DEFAULT 0,
    gross_amount     REAL    NOT NULL DEFAULT 0,
    fees             REAL    NOT NULL DEFAULT 0,
    taxes            REAL    NOT NULL DEFAULT 0,
    net_amount       REAL    NOT NULL DEFAULT 0,
    notes            TEXT
);

CREATE INDEX IF NOT EXISTS idx_transactions_date        ON transactions(date);
CREATE INDEX IF NOT EXISTS idx_transactions_type        ON transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_transactions_asset_class ON transactions(asset_class);
