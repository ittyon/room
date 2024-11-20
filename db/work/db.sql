use hashimoto_db;
select * from users;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL,
    password VARCHAR(50) NOT NULL,
    email VARCHAR(100),
    nickname VARCHAR(50)
);

insert into users(username, password, email, nickname) values
('itsuki', 'test001', 'negroponte8528@gmail.com', 'いっちょん'),
('miharu', 'test002',  '', 'みはころもち');

-------------------------

CREATE TABLE stock_transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stock_code CHAR(4) NOT NULL,
    transaction_type ENUM('buy', 'sell') NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL,
    transaction_date DATETIME NOT NULL,
    user_id INT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 正しいDATETIME形式で3行のテストデータを挿入する
INSERT INTO stock_transactions (stock_code, transaction_type, quantity, unit_price, transaction_date, user_id)
VALUES
('7203', 'buy', 100, 2300, '2023-10-20', 1),
('6758', 'sell', 50, 7000, '2023-10-19', 1),
('9984', 'buy', 200, 5500, '2023-10-18', 1);

delete from stock_transactions where id = 19;

select * from stock_transactions st
join users u on st.user_id = u.id
;

select 
	stock_code,
    user_id,
	sum(case when transaction_type = 'buy' then quantity end) - sum(case when transaction_type = 'sell' then quantity else 0 end) as hold_quantity
from stock_transactions
-- where stock_code = '1111' and  user_id = '1'
group by stock_code, user_id
;

-- 取引データ
select
	stock_code,
    case when transaction_type = 'buy' then '購入' else '売却' end,
    quantity,
    unit_price,
    DATE_FORMAT(transaction_date, '%Y/%m/%d')
from stock_transactions
where user_id = '1'
order by transaction_date desc, created_at desc
;


show databases;

select user, host from mysql.user;

-- すべてのホスト（%）からの接続を許可
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;

-- 権限をリロード
FLUSH PRIVILEGES;





CREATE TABLE stock (
    stock_code VARCHAR(4) PRIMARY KEY,           -- Codeの最初の4桁
    company_name VARCHAR(255) NOT NULL,          -- 会社名
    sector_name VARCHAR(255),                    -- Sector33CodeName
    INDEX idx_stock_code (stock_code)            -- stock_codeにインデックスを作成
);

drop table stock;

