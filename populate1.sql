CREATE TABLE IF NOT EXISTS currencies (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) NOT NULL,
    rate_usd NUMERIC NOT NULL,
    type VARCHAR(20) NOT NULL,
    update_time TIMESTAMP NOT NULL
);

INSERT INTO currencies (code, rate_usd, type, update_time) VALUES
    ('BRL', 0, 'REAL', '2024-01-01 00:00:00'),
    ('EUR', 0, 'REAL', '2024-01-01 00:00:00'),
    ('BTC', 0, 'REAL', '2024-01-01 00:00:00'),
    ('ETH', 0, 'REAL', '2024-01-01 00:00:00'),
    ('USD', 1, 'BACKING', '2024-01-01 00:00:00');