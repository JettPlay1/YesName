from dotenv import load_dotenv
load_dotenv()

from aiogram import F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command

from bot.keyboards import *
from bot import dp

@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer("Привет", reply_markup=main_menu_kb)

@dp.callback_query(F.data == "main_menu")
async def main_menu(callback: CallbackQuery):
    await callback.message.edit_text(text="Главное меню", reply_markup=main_menu_kb)

@dp.callback_query(F.data == "get_task")
async def get_task_command(callback: CallbackQuery):
    await callback.message.edit_text(text="Нажали Получить задание", reply_markup=return_back_kb)



@dp.callback_query(F.data == "get_listener")
async def get_listener_command(callback: CallbackQuery):
    await callback.message.edit_text(text="Нажали Получить слушателя", reply_markup=return_back_kb)


@dp.callback_query(F.data == "leave_feedback")
async def leave_feedback_command(callback: CallbackQuery):
    await callback.message.edit_text(text="Нажали Оставить фидбек", reply_markup=return_back_kb)