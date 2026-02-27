from sqlalchemy import create_engine, String, Float, Integer, BigInteger, Text, TIMESTAMP, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from libs.core.config import settings


engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


class Candle(Base):
    __tablename__ = "candles"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    market: Mapped[str] = mapped_column(String(10), index=True)   # spot|futures
    interval: Mapped[str] = mapped_column(String(10), index=True) # 15m|1h|4h
    open_time: Mapped[int] = mapped_column(BigInteger, index=True)  # epoch ms
    open: Mapped[float] = mapped_column(Float)
    high: Mapped[float] = mapped_column(Float)
    low: Mapped[float] = mapped_column(Float)
    close: Mapped[float] = mapped_column(Float)
    volume: Mapped[float] = mapped_column(Float)


class Signal(Base):
    __tablename__ = "signals"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    ts: Mapped[str] = mapped_column(TIMESTAMP(timezone=True), server_default=text("now()"), index=True)
    symbol: Mapped[str] = mapped_column(String(20), index=True)
    market: Mapped[str] = mapped_column(String(10), index=True)
    interval: Mapped[str] = mapped_column(String(10), index=True)
    bias: Mapped[str] = mapped_column(String(16))  # bullish|bearish|neutral
    score: Mapped[float] = mapped_column(Float)    # 0..100
    reasons: Mapped[str] = mapped_column(Text)     # json string for now


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
