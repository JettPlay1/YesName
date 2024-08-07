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
from db.classes import *
from bot.states import Form_send_flag

@dp.message(Command("start"))
async def start_command(message: Message):
    user_id = message.from_user.id
    user_data = await get_user_data(user_id)
    if user_data is None:
        await insert_user(user_id)

    user_data = await get_user_data(user_id)
    await get_random_task(user_id)

    await message.answer(f"Привет, {user_data['surname']} {user_data['name']}. У тебя {user_data['score']} поинтов!", 
                                    reply_markup=main_menu_kb)


@dp.callback_query(F.data == "main_menu")
async def main_menu(callback: CallbackQuery):
    user_data = await get_user_data(callback.from_user.id)

    await callback.message.edit_text(text=f"Привет, {user_data['name']} {user_data['surname']}. У тебя {user_data['score']} поинтов!", 
                                     reply_markup=main_menu_kb)


@dp.callback_query(F.data == "get_task")
async def get_task_command(callback: CallbackQuery):
    user_id = callback.from_user.id
    user_data = await get_user_data(user_id)
    if user_data['task_id'] == -1:
        await callback.message.edit_text(text=f"Сейчас у тебя нет задания для выполнения",
                                         reply_markup=return_back_kb)
        return
    task_data    = await get_task_data(user_data['task_id'])
    subtask_data = await get_subtask_data(user_data['subtask_id'])
    await callback.message.edit_text(text=f"<b>{task_data['theme']}</b>\n{subtask_data['name']}: {subtask_data['description']}", 
                                     reply_markup=flag_kb, 
                                     parse_mode='html')


@dp.callback_query(F.data == "rating")
async def get_listener_command(callback: CallbackQuery):
    users = await get_all_users()
    msg = "Рейтинг пользователей\n"
    for i, row in enumerate(users):
        msg += f"{i+1}. {row['surname']} {row['name']} - {row['score']} поинтов\n"
    
    await callback.message.edit_text(text=msg, 
                                     reply_markup=return_back_kb)


@dp.callback_query(F.data == "get_team")
async def get_team_command(callback: CallbackQuery):
    user_data = await get_user_data(callback.from_user.id)
    task_id = user_data['task_id']
    if task_id == -1:
        await callback.message.edit_text(text="У вас пока что нет команды",
                                         reply_markup=return_back_kb)
        return

    users = await get_all_users(User.task_id, task_id)
    msg = "Твоя команда:\n"
    for i, user in enumerate(users):
        user_data = await get_user_data(user['id'])
        msg += f"{i + 1}. {user_data['surname']} {user_data['name']}.\n"
    
    await callback.message.edit_text(text=msg, 
                                     reply_markup=return_back_kb)


@dp.callback_query(F.data == "achievements")
async def achievements_command(callback: CallbackQuery):
    await callback.message.edit_text(text="Нажали Ачивки", 
                                     reply_markup=return_back_kb)


@dp.callback_query(F.data == "shop")
async def shop_command(callback: CallbackQuery):
    await callback.message.edit_text(text="МАГАЗИН", 
                                     reply_markup=return_back_kb)


@form_router.callback_query(F.data == "send_flag")
async def send_flag_command(callback: CallbackQuery, state: FSMContext):
    user_data = await get_user_data(callback.from_user.id)
    if user_data['task_id'] == -1:
        await callback.message.edit_text(text="Вы уже решили это задание.", 
                                         reply_markup=return_back_kb)
        return
    await state.set_state(Form_send_flag.sending)
    await callback.message.answer(text="Введите флаг:")


@form_router.message(Form_send_flag.sending)
async def validate_flag(message: Message, state: FSMContext):
    await state.clear()
    flag = message.text
    user_id = message.from_user.id
    user_data = await get_user_data(user_id)
    subtask_data = await get_subtask_data(user_data['subtask_id'])
    task_data = await get_task_data(user_data['task_id'])
    if user_data['task_id'] == -1:
        await message.answer(text=f"Задание уже решено!",
                             reply_markup=return_back_kb)
        return
    if flag == subtask_data['flag']:
        flag_part = await get_flag_part(user_id, task_data['flag'])
        await message.answer(text=f"Верный флаг! Частичка настоящего флага:\n{flag_part[0]}. {flag_part[1]}", 
                             reply_markup=return_back_kb)
        return
    
    if flag == task_data['flag']:
        await update_after_validate(task_data)
        await message.answer(text=f"Верный флаг! Вам начислено {task_data['score']} поинтов.", 
                             reply_markup=return_back_kb)
        return
    
    await message.answer(text="Неправильный флаг", 
                         reply_markup=return_back_kb)


async def update_after_validate(task_data: dict):
    users = await get_all_users(User.task_id, task_data['id'])
    for user in users:
        await update_user_by_id(user['id'], User.score, user['score'] + task_data['score'])
        if user['completed_tasks']:
            await update_user_by_id(user['id'], User.completed_tasks, user['completed_tasks'] + ',' + str(task_data['id']))
        else:
            await update_user_by_id(user['id'], User.completed_tasks, str(task_data['id']))
        await update_user_by_id(user['id'], User.task_id, -1)