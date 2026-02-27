from datetime import datetime
import json
from fastapi import FastAPI, Query
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from libs.core.db import SessionLocal

app = FastAPI(title="360 Crypto Eye API", version="1.0.0")

@app.get("/health")
def health():
    return {"status": "ok"}

def _iso(v):
    return v.isoformat() if isinstance(v, datetime) else v

@app.get("/signals/latest")
def latest_signals(
    symbol: str | None = Query(default=None),
    market: str | None = Query(default=None),
    interval: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=500),
):
    where = []
    params = {"limit": limit}

    if symbol:
        where.append("symbol = :symbol")
        params["symbol"] = symbol.upper()
    if market:
        where.append("market = :market")
        params["market"] = market
    if interval:
        where.append('"interval" = :interval')
        params["interval"] = interval

    where_sql = f"WHERE {' AND '.join(where)}" if where else ""

    sql = text(f"""
        SELECT ts, market, symbol, "interval", candle_open_time, bias, score,
               CASE WHEN reasons IS NULL THEN NULL ELSE reasons::text END AS reasons
        FROM signals
        {where_sql}
        ORDER BY ts DESC
        LIMIT :limit
    """)

    db = SessionLocal()
    try:
        rows = db.execute(sql, params).mappings().all()
        items = []
        for r in rows:
            d = dict(r)
            d["ts"] = _iso(d.get("ts"))
            d["candle_open_time"] = _iso(d.get("candle_open_time"))
            if isinstance(d.get("reasons"), str):
                try:
                    d["reasons"] = json.loads(d["reasons"])
                except Exception:
                    pass
            items.append(d)
        return {"count": len(items), "items": items}
    except SQLAlchemyError as e:
        return {"count": 0, "items": [], "error": str(e)}
    finally:
        db.close()
