import asyncio
import json
from datetime import datetime, timezone

import redis
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from libs.core.config import settings
from libs.core.db import SessionLocal, Signal, Candle
from libs.core.logging import get_logger

logger = get_logger("signal-engine")
r = redis.Redis.from_url(settings.redis_url, decode_responses=True)

SYMBOLS = ["BTCUSDT", "ETHUSDT"]
INTERVALS = ["15m", "1h"]


def score_signal(last_close, ema20, ema50, rsi14):
    reasons = []
    score = 50.0

    if ema20 and ema50:
        if ema20 > ema50:
            score += 15
            reasons.append("EMA20 above EMA50 (bullish trend)")
        else:
            score -= 15
            reasons.append("EMA20 below EMA50 (bearish trend)")

    if last_close and ema20:
        if last_close > ema20:
            score += 10
            reasons.append("Price above EMA20")
        else:
            score -= 10
            reasons.append("Price below EMA20")

    if rsi14 is not None:
        if rsi14 < 30:
            score += 10
            reasons.append("RSI oversold bounce zone")
        elif rsi14 > 70:
            score -= 10
            reasons.append("RSI overbought pullback risk")
        else:
            reasons.append("RSI neutral")

    score = max(0, min(100, score))
    if score >= 60:
        bias = "bullish"
    elif score <= 40:
        bias = "bearish"
    else:
        bias = "neutral"

    return bias, score, reasons


def latest_candle_open_time(market, symbol, interval):
    db = SessionLocal()
    try:
        row = db.execute(
            select(Candle.open_time)
            .where(
                Candle.market == market,
                Candle.symbol == symbol,
                Candle.interval == interval,
            )
            .order_by(Candle.open_time.desc())
            .limit(1)
        ).first()
        return int(row[0]) if row else None
    finally:
        db.close()


def upsert_signal(symbol, market, interval, candle_open_time, bias, score, reasons):
    db = SessionLocal()
    try:
        stmt = pg_insert(Signal.__table__).values(
            ts=datetime.now(timezone.utc),
            symbol=symbol,
            market=market,
            interval=interval,
            candle_open_time=candle_open_time,
            bias=bias,
            score=score,
            reasons=json.dumps(reasons),
        ).on_conflict_do_nothing(
            index_elements=["market", "symbol", "interval", "candle_open_time"]
        )
        res = db.execute(stmt)
        db.commit()
        return res.rowcount or 0
    finally:
        db.close()


async def run_once():
    made = 0
    for market in ["spot", "futures"]:
        for symbol in SYMBOLS:
            for interval in INTERVALS:
                key = f"features:{market}:{symbol}:{interval}"
                raw = r.get(key)
                if not raw:
                    continue
                feat = json.loads(raw)

                cot = latest_candle_open_time(market, symbol, interval)
                if cot is None:
                    continue

                bias, score, reasons = score_signal(
                    feat.get("last_close"),
                    feat.get("ema20"),
                    feat.get("ema50"),
                    feat.get("rsi14"),
                )
                inserted = upsert_signal(symbol, market, interval, cot, bias, score, reasons)
                made += inserted
                logger.info(f"{market} {symbol} {interval} candle={cot} => {bias} ({score}) inserted={inserted}")
    logger.info(f"signal cycle done, inserted={made}")


async def run():
    logger.info("Signal engine started")
    while True:
        try:
            await run_once()
        except Exception as e:
            logger.exception(f"signal cycle failed: {e}")
        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(run())
