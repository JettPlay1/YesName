import asyncio

from bot import dp, tgbot
from bot.routes import *
from db import init_db
import logging

logging.basicConfig(level=logging.INFO)

async def main():
    await init_db()
    await dp.start_polling(tgbot)


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
