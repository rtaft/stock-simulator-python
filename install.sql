CREATE DATABASE IF NOT EXISTS stocks;
USE stocks;
GRANT ALL PRIVILEGES ON stocks.* TO '<SETUSER>'@'localhost' IDENTIFIED BY '<SETPASS>';

CREATE TABLE IF NOT EXISTS company (
    company_id INT AUTO_INCREMENT,
    company_name VARCHAR(100),
    ticker VARCHAR(10) NOT NULL,
    exchange VARCHAR(10) NOT NULL,
    PRIMARY KEY(company_id)
);

CREATE TABLE IF NOT EXISTS history (
    history_id INT AUTO_INCREMENT,
    company_id INT NOT NULL,
    trade_date DATE NOT NULL,
    trade_close FLOAT NOT NULL,
    trade_volume INT NOT NULL,
    PRIMARY KEY(history_id),
    FOREIGN KEY(company_id) REFERENCES company(company_id)
);
