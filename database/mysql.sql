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
    FOREIGN KEY(company_id) REFERENCES company(company_id),
    UNIQUE KEY (company_id, trade_date)
);

CREATE TABLE IF NOT EXISTS dividend_history (
    dividend_id INT AUTO_INCREMENT,
    company_id INT NOT NULL,
    ex_date DATE,
    dividend FLOAT NOT NULL,
    PRIMARY KEY(dividend_id),
    FOREIGN KEY(company_id) REFERENCES company(company_id)
);

CREATE TABLE IF NOT EXISTS split_history (
    split_id INT AUTO_INCREMENT,
    company_id INT NOT NULL,
    split_date DATE,
    ratio FLOAT NOT NULL,
    PRIMARY KEY(split_id),
    FOREIGN KEY(company_id) REFERENCES company(company_id)
);

CREATE TABLE IF NOT EXISTS stock_list (
    list_id INT AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    PRIMARY KEY (list_id)
);

CREATE TABLE IF NOT EXISTS stock_list_data (
    data_id INT AUTO_INCREMENT,
    company_id INT NOT NULL,
    list_id INT NOT NULL,
    date_added DATE,
    date_removed DATE,
    PRIMARY KEY (data_id),
    FOREIGN KEY(company_id) REFERENCES company(company_id),
    FOREIGN KEY(list_id) REFERENCES stock_list(list_id)
);

CREATE TABLE IF NOT EXISTS traders (
    trader_id INT AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    location VARCHAR(2000) NOT NULL,
    
    PRIMARY KEY (trader_id)
);

CREATE TABLE IF NOT EXISTS simulation (
    simulation_id INT AUTO_INCREMENT,
    simulation_date DATE NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    starting_balance FLOAT NOT NULL,
    description VARCHAR(2000),
    PRIMARY KEY (simulation_id)
);

CREATE TABLE IF NOT EXISTS simulation_trader (
    simulation_trader_id INT AUTO_INCREMENT,
    simulation_id INT NOT NULL,
    trader_id INT NOT NULL,
    PRIMARY KEY (simulation_trader_id),
    FOREIGN KEY (simulation_id) REFERENCES simulation(simulation_id),
    FOREIGN KEY (trader_id) REFERENCES traders(trader_id),
    UNIQUE KEY (simulation_id, trader_id)
);

CREATE TABLE IF NOT EXISTS transaction (
    transaction_id INT AUTO_INCREMENT,
    simulation_trader_id INT NOT NULL,
    transaction_date TIMESTAMP NOT NULL,
    transaction_price FLOAT NOT NULL,
    transaction_type VARCHAR(10) NOT NULL,
    transaction_quantity FLOAT NOT NULL,
    symbol VARCHAR(10) NOT NULL,
    PRIMARY KEY (transaction_id),
    FOREIGN KEY (simulation_trader_id) REFERENCES simulation_trader(simulation_trader_id)
);