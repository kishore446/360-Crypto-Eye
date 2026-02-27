from telegram import Bot
from libs.core.config import settings


class TelegramAdapter:
    def __init__(self) -> None:
        self.bot = Bot(token=settings.telegram_bot_token)

    def _chat_id(self, channel: str) -> str:
        if channel == "spot":
            return settings.telegram_spot_chat_id
        if channel == "futures":
            return settings.telegram_futures_chat_id
        raise ValueError("channel must be 'spot' or 'futures'")

    async def send_text(self, channel: str, text: str) -> None:
        await self.bot.send_message(chat_id=self._chat_id(channel), text=text)

    async def send_photo(self, channel: str, photo_path: str, caption: str = "") -> None:
        with open(photo_path, "rb") as f:
            await self.bot.send_photo(chat_id=self._chat_id(channel), photo=f, caption=caption)
