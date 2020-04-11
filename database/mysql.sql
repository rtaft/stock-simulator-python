CREATE TABLE IF NOT EXISTS company (
    company_id INT AUTO_INCREMENT,
    company_name VARCHAR(100),
    symbol VARCHAR(10) NOT NULL,
    exchange VARCHAR(10) NOT NULL,
    ipo INT,
    sector VARCHAR(60),
    industry VARCHAR(255),
    error CHAR(1) default null;
    PRIMARY KEY(company_id)
);

CREATE TABLE `price_history` (
  `company_id` int(11) NOT NULL,
  `trade_date` date NOT NULL,
  `trade_close` float NOT NULL,
  `trade_volume` int(11) NOT NULL,
  KEY `trade_date_index` (`trade_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
/*!50100 PARTITION BY RANGE (YEAR(trade_date))
(PARTITION p1960 VALUES LESS THAN (1980) ENGINE = InnoDB,
 PARTITION p1980 VALUES LESS THAN (1985) ENGINE = InnoDB,
 PARTITION p1985 VALUES LESS THAN (1990) ENGINE = InnoDB,
 PARTITION p1990 VALUES LESS THAN (1991) ENGINE = InnoDB,
 PARTITION p1991 VALUES LESS THAN (1992) ENGINE = InnoDB,
 PARTITION p1992 VALUES LESS THAN (1993) ENGINE = InnoDB,
 PARTITION p1993 VALUES LESS THAN (1994) ENGINE = InnoDB,
 PARTITION p1994 VALUES LESS THAN (1995) ENGINE = InnoDB,
 PARTITION p1995 VALUES LESS THAN (1996) ENGINE = InnoDB,
 PARTITION p1996 VALUES LESS THAN (1997) ENGINE = InnoDB,
 PARTITION p1997 VALUES LESS THAN (1998) ENGINE = InnoDB,
 PARTITION p1998 VALUES LESS THAN (1999) ENGINE = InnoDB,
 PARTITION p1999 VALUES LESS THAN (2000) ENGINE = InnoDB,
 PARTITION p2000 VALUES LESS THAN (2001) ENGINE = InnoDB,
 PARTITION p2001 VALUES LESS THAN (2002) ENGINE = InnoDB,
 PARTITION p2002 VALUES LESS THAN (2003) ENGINE = InnoDB,
 PARTITION p2003 VALUES LESS THAN (2004) ENGINE = InnoDB,
 PARTITION p2004 VALUES LESS THAN (2005) ENGINE = InnoDB,
 PARTITION p2005 VALUES LESS THAN (2006) ENGINE = InnoDB,
 PARTITION p2006 VALUES LESS THAN (2007) ENGINE = InnoDB,
 PARTITION p2007 VALUES LESS THAN (2008) ENGINE = InnoDB,
 PARTITION p2008 VALUES LESS THAN (2009) ENGINE = InnoDB,
 PARTITION p2009 VALUES LESS THAN (2010) ENGINE = InnoDB,
 PARTITION p2010 VALUES LESS THAN (2011) ENGINE = InnoDB,
 PARTITION p2011 VALUES LESS THAN (2012) ENGINE = InnoDB,
 PARTITION p2012 VALUES LESS THAN (2013) ENGINE = InnoDB,
 PARTITION p2013 VALUES LESS THAN (2014) ENGINE = InnoDB,
 PARTITION p2014 VALUES LESS THAN (2015) ENGINE = InnoDB,
 PARTITION p2015 VALUES LESS THAN (2016) ENGINE = InnoDB,
 PARTITION p2016 VALUES LESS THAN (2017) ENGINE = InnoDB,
 PARTITION p2017 VALUES LESS THAN (2018) ENGINE = InnoDB,
 PARTITION p2018 VALUES LESS THAN (2019) ENGINE = InnoDB,
 PARTITION p2019 VALUES LESS THAN (2020) ENGINE = InnoDB,
 PARTITION p2020 VALUES LESS THAN (2021) ENGINE = InnoDB,
 PARTITION p2021 VALUES LESS THAN (2022) ENGINE = InnoDB) */

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
    simulation_date TIMESTAMP NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    starting_balance FLOAT NOT NULL,
    description VARCHAR(2000),
    stock_list VARCHAR(50) NOT NULL,
    PRIMARY KEY (simulation_id)
);

CREATE TABLE IF NOT EXISTS simulation_trader (
    simulation_trader_id INT AUTO_INCREMENT,
    simulation_id INT NOT NULL,
    trader_id INT NOT NULL,
    ending_value FLOAT,
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
    transaction_total FLOAT NOT NULL,
    company_id INT NOT NULL,
    PRIMARY KEY (transaction_id),
    FOREIGN KEY (simulation_trader_id) REFERENCES simulation_trader(simulation_trader_id),
    FOREIGN KEY (company_id) REFERENCES company(company_id)
);
