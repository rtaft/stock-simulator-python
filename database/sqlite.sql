CREATE TABLE IF NOT EXISTS company (
    company_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    company_name VARCHAR(100),
    symbol VARCHAR(10) NOT NULL,
    exchange VARCHAR(10) NOT NULL,
    ipo INTEGER,
    sector VARCHAR(60),
    industry VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS price_history (
    history_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    company_id INTEGER NOT NULL,
    trade_date DATE NOT NULL,
    trade_close FLOAT NOT NULL,
    trade_volume INTEGER NOT NULL,
    FOREIGN KEY(company_id) REFERENCES company(company_id)
);

CREATE TABLE IF NOT EXISTS dividend_history (
    dividend_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    ex_date TIMESTAMP,
    dividend FLOAT NOT NULL,
    company_id INTEGER NOT NULL,
    FOREIGN KEY(company_id) REFERENCES company(company_id)
);
