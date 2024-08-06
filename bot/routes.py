from dotenv import load_dotenv
load_dotenv()

import logging
from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from bot.keyboards import *
from bot import dp, form_router

from db.queries import *
from bot.states import Form_send_flag

@dp.message(Command("start"))
async def start_command(message: Message):
    user_id = message.from_user.id
    await add_user(user_id)
    user_data = await get_user_stats(user_id)

    await message.answer(f"Привет, {user_data[1]} {user_data[0]}. У тебя {user_data[2]} поинтов!", reply_markup=main_menu_kb)


@dp.callback_query(F.data == "main_menu")
async def main_menu(callback: CallbackQuery):
    user_data = await get_user_stats(callback.from_user.id)

    await callback.message.edit_text(text=f"Привет, {user_data[1]} {user_data[0]}. У тебя {user_data[2]} поинтов!", reply_markup=main_menu_kb)


@dp.callback_query(F.data == "get_task")
async def get_task_command(callback: CallbackQuery):
    user_id = callback.from_user.id
    task_name = await get_task(user_id)
    await callback.message.edit_text(text=f"{task_name}", reply_markup=flag_kb)


@dp.callback_query(F.data == "rating")
async def get_listener_command(callback: CallbackQuery):
    users = await get_top()
    msg = "Рейтинг пользователей\n"
    for i, row in enumerate(users):
        msg += f"{i+1}. {row[1]} {row[0]} - {row[2]} поинтов\n"
    
    await callback.message.edit_text(text=msg, reply_markup=return_back_kb)


@dp.callback_query(F.data == "get_team")
async def leave_feedback_command(callback: CallbackQuery):
    user_id = callback.from_user.id
    task_id = await get_user_task_id(user_id)
    users = await get_users_on_task(task_id)
    msg = "Твоя команда:\n"
    for i, id in enumerate(users):
        if user_id == id:
            continue
        user_data = await get_user_stats(id)
        msg += f"{i + 1}. {user_data[1]} {user_data[0]}.\n"
    
    await callback.message.edit_text(text=msg, reply_markup=return_back_kb)


@dp.callback_query(F.data == "achievements")
async def leave_feedback_command(callback: CallbackQuery):
    await callback.message.edit_text(text="Нажали Ачивки", reply_markup=return_back_kb)


@dp.callback_query(F.data == "shop")
async def main_menu(callback: CallbackQuery):
    await callback.message.edit_text(text="МАГАЗИН", reply_markup=return_back_kb)


@form_router.callback_query(F.data == "send_flag")
async def send_flag_command(callback: CallbackQuery, state: FSMContext):
    is_solved = await is_task_solved(callback.from_user.id)
    print(is_solved)
    if is_solved:
        await callback.message.edit_text(text="Вы уже решили это задание.", reply_markup=return_back_kb)
        return
    await state.set_state(Form_send_flag.sending)
    await callback.message.answer(text="Введите флаг:")


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
        score = await get_task_score(user_id)
        await add_points_to_user(user_id, score)
        await mark_task_completed(user_id)
        await message.answer(text=f"Верный флаг! Вам начислено {score} поинтов.", reply_markup=return_back_kb)
        return
    
    await message.answer(text="Неправильный флаг", reply_markup=return_back_kb)