import asyncio
from libs.core.logging import get_logger

logger = get_logger("publisher")


async def run() -> None:
    logger.info("Publisher service started")
    while True:
        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(run())
