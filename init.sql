CREATE TABLE app_user (user_id INT NOT NULL AUTO_INCREMENT, username VARCHAR(45) NOT NULL, password VARCHAR(80) NOT NULL, full_name VARCHAR(45) NOT NULL, email VARCHAR(80) NOT NULL UNIQUE, PRIMARY KEY (user_id));

CREATE TABLE search_history (id int NOT NULL AUTO_INCREMENT, user_id INT NOT NULL, etf VARCHAR(4) NOT NULL, timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (id));

CREATE TABLE top_holdings_entry (id INT NOT NULL AUTO_INCREMENT, etf VARCHAR(4) NOT NULL, holding VARCHAR(45) NOT NULL, weight DECIMAL(5,2) NOT NULL, shares INT NOT NULL, primary key (id));

create table country_weights_entry (id INT NOT NULL AUTO_INCREMENT, etf VARCHAR(4) NOT NULL, country VARCHAR(45) NOT NULL, weight DECIMAL(5,2) NOT NULL, primary key (id));

create table sector_weights_entry (id INT NOT NULL AUTO_INCREMENT, etf VARCHAR(4) NOT NULL, sector VARCHAR(45) NOT NULL, weight DECIMAL(5,2) NOT NULL, primary key (id));