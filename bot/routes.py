from dotenv import load_dotenv
load_dotenv()

import logging
from aiogram import F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command

from bot.keyboards import *
from bot import dp

from db.queries import add_user, get_task


@dp.message(Command("start"))
async def start_command(message: Message):
    user_id = message.from_user.id
    await add_user(user_id)
    await message.answer("Привет", reply_markup=main_menu_kb)


@dp.callback_query(F.data == "main_menu")
async def main_menu(callback: CallbackQuery):
    await callback.message.edit_text(text="Главное меню", reply_markup=main_menu_kb)


@dp.callback_query(F.data == "get_task")
async def get_task_command(callback: CallbackQuery):
    user_id = callback.from_user.id
    task_name = await get_task(user_id)
    await callback.message.edit_text(text=f"{task_name}", reply_markup=return_back_kb)


@dp.callback_query(F.data == "rating")
async def get_listener_command(callback: CallbackQuery):
    await callback.message.edit_text(text="Нажали Рейтинг", reply_markup=return_back_kb)


@dp.callback_query(F.data == "achievements")
async def leave_feedback_command(callback: CallbackQuery):
    await callback.message.edit_text(text="Нажали Ачивки", reply_markup=return_back_kb)


@dp.callback_query(F.data == "shop")
async def main_menu(callback: CallbackQuery):
    await callback.message.edit_text(text="МАГАЗИН", reply_markup=return_back_kb)