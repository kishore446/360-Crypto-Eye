import asyncio
from libs.core.logging import get_logger

logger = get_logger("chart_renderer")


async def run() -> None:
    logger.info("Chart renderer started")
    while True:
        await asyncio.sleep(10)


if __name__ == "__main__":
    asyncio.run(run())
