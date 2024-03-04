-- Verifica se a tabela currencies está vazia
SELECT count(*) FROM currencies;

-- Se a contagem for zero, insere os dados de exemplo
INSERT INTO currencies (code, rate_usd, type, update_time)
SELECT 'BRL', 0, 'real', '2024-01-01 00:00:00'
WHERE NOT EXISTS (SELECT 1 FROM currencies);

INSERT INTO currencies (code, rate_usd, type, update_time)
SELECT 'EUR', 0, 'real', '2024-01-01 00:00:00'
WHERE NOT EXISTS (SELECT 1 FROM currencies WHERE code = 'EUR');

INSERT INTO currencies (code, rate_usd, type, update_time)
SELECT 'BTC', 0, 'real', '2024-01-01 00:00:00'
WHERE NOT EXISTS (SELECT 1 FROM currencies WHERE code = 'BTC');

INSERT INTO currencies (code, rate_usd, type, update_time)
SELECT 'ETH', 0, 'real', '2024-01-01 00:00:00'
WHERE NOT EXISTS (SELECT 1 FROM currencies WHERE code = 'ETH');

INSERT INTO currencies (code, rate_usd, type, update_time)
SELECT 'USD', 1, 'backing', '2024-01-01 00:00:00'
WHERE NOT EXISTS (SELECT 1 FROM currencies WHERE code = 'USD');