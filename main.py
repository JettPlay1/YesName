import asyncio

from bot import dp, tgbot
from bot.routes import *
import logging


logging.basicConfig(level=logging.INFO)

async def main():
    await dp.start_polling(tgbot)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
