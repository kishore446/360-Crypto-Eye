import asyncio
import json
from collections import defaultdict

import redis
from sqlalchemy import select

from libs.core.config import settings
from libs.core.db import SessionLocal, Candle
from libs.core.logging import get_logger

logger = get_logger("feature-engine")
r = redis.Redis.from_url(settings.redis_url, decode_responses=True)

SYMBOLS = ["BTCUSDT", "ETHUSDT"]
INTERVALS = ["15m", "1h"]


def ema(values, period):
    if len(values) < period:
        return None
    k = 2 / (period + 1)
    e = sum(values[:period]) / period
    for v in values[period:]:
        e = (v * k) + (e * (1 - k))
    return e


def rsi(values, period=14):
    if len(values) < period + 1:
        return None
    gains, losses = [], []
    for i in range(1, len(values)):
        d = values[i] - values[i - 1]
        gains.append(max(d, 0))
        losses.append(abs(min(d, 0)))
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))


def load_closes(market, symbol, interval, limit=250):
    db = SessionLocal()
    try:
        rows = db.execute(
            select(Candle.close)
            .where(
                Candle.market == market,
                Candle.symbol == symbol,
                Candle.interval == interval,
            )
            .order_by(Candle.open_time.desc())
            .limit(limit)
        ).all()
        closes = [float(x[0]) for x in rows][::-1]
        return closes
    finally:
        db.close()


async def compute_once():
    total = 0
    for market in ["spot", "futures"]:
        for symbol in SYMBOLS:
            for interval in INTERVALS:
                closes = load_closes(market, symbol, interval)
                if len(closes) < 60:
                    continue

                payload = {
                    "ema20": ema(closes, 20),
                    "ema50": ema(closes, 50),
                    "rsi14": rsi(closes, 14),
                    "last_close": closes[-1],
                }
                key = f"features:{market}:{symbol}:{interval}"
                r.set(key, json.dumps(payload))
                total += 1
                logger.info(f"updated {key} -> {payload}")

    logger.info(f"feature cycle done, keys={total}")


async def run():
    logger.info("Feature engine started")
    while True:
        try:
            await compute_once()
        except Exception as e:
            logger.exception(f"feature cycle failed: {e}")
        await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(run())
