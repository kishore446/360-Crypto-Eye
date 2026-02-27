import asyncio
import httpx
from sqlalchemy import select
from libs.core.logging import get_logger
from libs.core.db import init_db, SessionLocal, Candle

logger = get_logger("ingestion")

SPOT_URL = "https://api.binance.com/api/v3/klines"
FUTURES_URL = "https://fapi.binance.com/fapi/v1/klines"

SYMBOLS = ["BTCUSDT", "ETHUSDT"]
INTERVALS = ["15m", "1h"]
LIMIT = 200


def to_float(v) -> float:
    return float(v)


async def fetch_klines(client: httpx.AsyncClient, market: str, symbol: str, interval: str):
    url = SPOT_URL if market == "spot" else FUTURES_URL
    params = {"symbol": symbol, "interval": interval, "limit": LIMIT}
    r = await client.get(url, params=params, timeout=20.0)
    r.raise_for_status()
    return r.json()


def upsert_candles(rows, market: str, symbol: str, interval: str):
    db = SessionLocal()
    inserted = 0
    try:
        for k in rows:
            open_time = int(k[0])

            exists = db.execute(
                select(Candle.id).where(
                    Candle.market == market,
                    Candle.symbol == symbol,
                    Candle.interval == interval,
                    Candle.open_time == open_time,
                )
            ).first()

            if exists:
                continue

            c = Candle(
                market=market,
                symbol=symbol,
                interval=interval,
                open_time=open_time,
                open=to_float(k[1]),
                high=to_float(k[2]),
                low=to_float(k[3]),
                close=to_float(k[4]),
                volume=to_float(k[5]),
            )
            db.add(c)
            inserted += 1

        db.commit()
    finally:
        db.close()
    return inserted


async def ingest_once():
    total = 0
    async with httpx.AsyncClient() as client:
        for market in ["spot", "futures"]:
            for symbol in SYMBOLS:
                for interval in INTERVALS:
                    try:
                        rows = await fetch_klines(client, market, symbol, interval)
                        n = upsert_candles(rows, market, symbol, interval)
                        total += n
                        logger.info(f"{market} {symbol} {interval}: +{n} candles")
                    except Exception as e:
                        logger.exception(f"ingest failed for {market} {symbol} {interval}: {e}")
    logger.info(f"ingest cycle done, inserted={total}")


async def run() -> None:
    init_db()
    logger.info("Ingestion service started (db initialized)")
    while True:
        await ingest_once()
        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(run())
