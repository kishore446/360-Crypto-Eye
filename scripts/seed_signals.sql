INSERT INTO signals (market, symbol, "interval", candle_open_time, bias, score, reasons)
VALUES
('spot','BTCUSDT','15m', now() - interval '15 minutes','bullish', 0.82, '{"rsi": 61, "macd": "cross_up"}'),
('futures','ETHUSDT','15m', now() - interval '15 minutes','bearish', 0.71, '{"rsi": 42, "macd": "cross_down"}'),
('spot','SOLUSDT','5m', now() - interval '5 minutes','bullish', 0.64, '{"breakout": true}')
ON CONFLICT DO NOTHING;
