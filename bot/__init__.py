from dotenv import load_dotenv
load_dotenv()
import os

from aiogram import Bot, Dispatcher, Router
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from bot.keyboards import *

TG_TOKEN = os.getenv("TOKEN")
tgbot = Bot(token=TG_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
