CREATE TABLE IF NOT EXISTS signals (
  ts TIMESTAMPTZ NOT NULL DEFAULT now(),
  market TEXT,
  symbol TEXT,
  "interval" TEXT,
  candle_open_time TIMESTAMPTZ,
  bias TEXT,
  score DOUBLE PRECISION,
  reasons JSONB
);

CREATE INDEX IF NOT EXISTS idx_signals_ts ON signals (ts DESC);
CREATE INDEX IF NOT EXISTS idx_signals_symbol ON signals (symbol);
