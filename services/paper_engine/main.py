import asyncio
from libs.core.logging import get_logger

logger = get_logger("paper_engine")


async def run() -> None:
    logger.info("Paper engine started")
    while True:
        await asyncio.sleep(30)


if __name__ == "__main__":
    asyncio.run(run())
