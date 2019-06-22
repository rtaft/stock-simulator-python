CREATE TABLE IF NOT EXISTS company (
    company_id INT AUTO_INCREMENT,
    company_name VARCHAR(100),
    symbol VARCHAR(10) NOT NULL,
    exchange VARCHAR(10) NOT NULL,
    ipo INT,
    sector VARCHAR(60),
    industry VARCHAR(255),
    PRIMARY KEY(company_id)
);

CREATE TABLE IF NOT EXISTS price_history (
    history_id INT AUTO_INCREMENT,
    company_id INT NOT NULL,
    trade_date DATE NOT NULL,
    trade_close FLOAT NOT NULL,
    trade_volume INT NOT NULL,
    PRIMARY KEY(history_id),
    FOREIGN KEY(company_id) REFERENCES company(company_id)
);

CREATE TABLE IF NOT EXISTS dividend_history (
    dividend_id INT AUTO_INCREMENT,
    ex_date TIMESTAMP,
    dividend FLOAT NOT NULL,
    company_id INT NOT NULL,
    PRIMARY KEY(dividend_id),
    FOREIGN KEY(company_id) REFERENCES company(company_id)
);