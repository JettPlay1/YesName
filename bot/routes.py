from dotenv import load_dotenv
load_dotenv()

import logging
from aiogram import F
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.keyboards import *
from bot import dp, form_router, tgbot

from db.queries import *
from bot.states import Form_send_flag

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
    await callback.message.edit_text(text=f"{task_name}", reply_markup=flag_kb)


@dp.callback_query(F.data == "rating")
async def get_listener_command(callback: CallbackQuery):
    await callback.message.edit_text(text="Нажали Рейтинг", reply_markup=return_back_kb)


@dp.callback_query(F.data == "achievements")
async def leave_feedback_command(callback: CallbackQuery):
    await callback.message.edit_text(text="Нажали Ачивки", reply_markup=return_back_kb)


@dp.callback_query(F.data == "shop")
async def main_menu(callback: CallbackQuery):
    await callback.message.edit_text(text="МАГАЗИН", reply_markup=return_back_kb)


@form_router.callback_query(F.data == "send_flag")
async def send_flag_command(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Form_send_flag.sending)
    await callback.message.edit_text(text="Введите флаг:", reply_markup=empty_kb)


@form_router.message(Form_send_flag.sending)
async def validate_flag(message: Message, state: FSMContext):
    await state.clear()
    flag = message.text
    user_id = message.from_user.id
    task_flag = await get_flag(user_id)
    task_real_flag = await get_real_flag(user_id)
    if flag == task_flag:
        flag_part = await get_flag_part(user_id, task_real_flag)
        await message.answer(text=f"Верный флаг! Частичка настоящего флага:\n{flag_part[0]}. {flag_part[1]}", reply_markup=return_back_kb)
        return
    if flag == task_real_flag:
        await message.answer(text="Верный флаг! Вам начислено...", reply_markup=return_back_kb)
        return
    await message.answer(text="Неправильный флаг", reply_markup=return_back_kb)
