from dotenv import load_dotenv
load_dotenv()

import logging
from aiogram import F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext

from bot.keyboards import *
from bot import dp, form_router
from bot.states import *

from db.queries import *
from db.classes import *


class ShopCallback(CallbackData, prefix="buy"):
    action: str
    index: int

@dp.message(Command("start"))
async def start_command(message: Message):
    user_id = message.from_user.id
    user_data = await get_user_data(user_id)
    if user_data is None:
        await insert_user(user_id)
        await get_random_task(user_id)

    user_data = await get_user_data(user_id)
    users = await get_all_users()
    task = await get_task_data(user_data['task_id'])
    if task == None:
        task = "нет темы"
    else:
        task = task['theme']
    place = 1
    for i, user in enumerate(users):
        if user_id == user['score']:
            place = i + 1
            break
    
    await message.answer(f"<b>{user_data['prefix']}{user_data['surname']} {user_data['name']}</b>\n\n" \
                         f"🏆 Личная статистика:\n" \
                         f"🔸 {place} место, {user_data['score']} баллов\n" \
                         f"🌟 Доступно MInCoin's: {user_data['mincoins']}\n\n" \
                         f"📋 Текущая тема: {task}\n\n"\
                         f"🏅Получено ачивок: 0", 
                         reply_markup=main_menu_kb,
                         parse_mode='HTML')


@dp.callback_query(F.data == "main_menu")
async def main_menu(callback: CallbackQuery):
    user_data = await get_user_data(callback.from_user.id)
    users = await get_all_users()
    task = await get_task_data(user_data['task_id'])
    if task == None:
        task = "нет темы"
    else:
        task = task['theme']
    place = 1
    for i, user in enumerate(users):
        if callback.from_user.id == user['score']:
            place = i + 1
            break
    await callback.message.edit_text(f"<b>{user_data['prefix']}{user_data['surname']} {user_data['name']}</b>\n\n" \
                                     f"🏆 Личная статистика:\n" \
                                     f"🔸 Личный рейтинг: {place} место, {user_data['score']} баллов\n" \
                                     f"🌟 Доступно MinCoin's: {user_data['mincoins']}\n\n" \
                                     f"📋 Текущая тема: {task}\n\n"\
                                     f"🏅Получено ачивок: 0", 
                                     reply_markup=main_menu_kb,
                                     parse_mode='HTML')


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
    await callback.message.edit_text(text=f"<b>Тема: {task_data['theme']}</b>\n{subtask_data['name']}: {subtask_data['description']}", 
                                     reply_markup=flag_kb, 
                                     parse_mode='html')


@dp.callback_query(F.data == "rating")
async def get_listener_command(callback: CallbackQuery):
    users = await get_all_users()
    msg = "🎖️ <b>Рейтинг пользователей:</b>\n\n"
    for i, row in enumerate(users):
        msg += f"<b>{i+1}.</b> {row['prefix']}{row['surname']} {row['name']}: {row['score']} баллов\n\n"
    
    await callback.message.edit_text(text=msg, 
                                     reply_markup=return_back_kb,
                                     parse_mode='HTML')


@dp.callback_query(F.data == "achievements")
async def achievements_command(callback: CallbackQuery):
    await callback.message.answer_sticker("CAACAgIAAxkBAAEavP9msvYWscIg0KAShxbTvrzwSt0tXQAC8U0AAvDbmUmtWLDWrAj3xDUE")
    await callback.message.answer(text="👷🏻‍♂️Ачивок пока нет,👷🏻‍♂️👷🏻‍♂️ ведутся технические👷🏻‍♂️ работы...👷🏻‍♂️👷🏻‍♂️👷🏻‍♂️", 
                                     reply_markup=return_back_kb)


@dp.callback_query(F.data == "shop")
async def shop_command(callback: CallbackQuery):
    goods = await get_all_goods()
    inline_keyboard = []
    for good in goods:
        inline_keyboard.append([InlineKeyboardButton(text=f"{good['name']} {good['price']} MinCoin's", callback_data=ShopCallback(action='buy', index=good['id']).pack())])
    inline_keyboard.append([InlineKeyboardButton(text="Назад", callback_data="main_menu")])
    kb = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    await callback.message.edit_text(text=f'👑 <b>Магазин кайфовых плюшек</b> 👑\n\n'\
                                          f'Здесь вы можете купить кастомизацию профиля на дашборде или хинты для тасков.', 
                                     reply_markup=kb,
                                     parse_mode='HTML')


@dp.callback_query(ShopCallback.filter(F.action == "buy"))
async def buy_good(callback: CallbackQuery):
    goods = await get_all_goods()
    user = await get_user_data(callback.from_user.id)
    good_idx = int(callback.data.split(':')[-1]) - 1
    if user['mincoins'] >= goods[good_idx]['price']:
        await update_user_by_id(callback.from_user.id, User.prefix, goods[good_idx]['prefix'])
        await update_user_by_id(callback.from_user.id, User.score, user['mincoins'] - goods[good_idx]['price'])
        await callback.message.edit_text(text=f"🎉 Подзравляем с покупкой {goods[good_idx]['name']}!",
                                         reply_markup=return_back_kb)
        return
    else:
        await callback.message.edit_text(text=f"😱 У вас не хватает очков для покупки:(",
                                         reply_markup=return_back_kb)
        return


@dp.callback_query(F.data == "exchange_points")
async def exchange_command(callback: CallbackQuery, state: FSMContext):
    user_data = await get_user_data(callback.from_user.id)
    points = user_data["score"]
    mincoins = user_data["mincoins"]
    await callback.message.edit_text(text=f"💱 <b>ОБМЕННИК</b>\n\n"\
                                          f"Здесь вы може обменять ваши баллы на MinCoin-ы по курсу 10:1\n\n"\
                                          f"💳<b>Баланс:</b> "\
                                          f"{points} баллов\t"\
                                          f"{mincoins} MinCoin's",
                                          reply_markup=exchenge_kb)


@form_router.callback_query(F.data == "exchange")
async def get_points_value(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Form_exchange_points.exchanging)
    await callback.message.answer("Введите сумму для обмена:")


@form_router.message(Form_exchange_points.exchanging)
async def exchange(message: Message, state: FSMContext):
    await state.clear()
    score = message.text
    user_data = await get_user_data(message.from_user.id)
    if not score.isdigit():
        await message.answer(text="Некорректная сумма...",
                             reply_markup=return_back_kb)
        return
    if int(score) <= 0:
        await message.answer(text="Некорректная сумма...",
                             reply_markup=return_back_kb)
        return
    if user_data['score'] < int(score):
        await message.answer(text="Недостаточно средств для обмена",
                             reply_markup=return_back_kb)
        return
    
    await update_user_by_id(message.from_user.id, User.score, user_data['score'] - int(score))
    await update_user_by_id(message.from_user.id, User.mincoins, user_data['mincoins'] + (int(score) // 10))
    await message.answer_sticker("CAACAgIAAxkBAAEavPVmsvE8gQuOJg6Da_Hm9WX3GN8k5gACNUoAAsVamUnsRKF0Tr1IxzUE")
    await message.answer(text=f"Вы обменяли {score} баллов на {int(score) // 10} MinCoin's\n\n"\
                               "<b>Осознанное вложение</b>",
                               reply_markup=return_back_kb,
                               parse_mode="HTML")


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
                             reply_markup=return_to_task_kb)
        return
    if flag == subtask_data['flag']:
        flag_part = await get_flag_part(user_id, task_data['flag'])
        await message.answer(text=f"🤙 Верный флаг! Частичка настоящего флага (Вторую заберёшь у друга):\n{flag_part[0]}. {flag_part[1]}", 
                             reply_markup=return_to_task_kb)
        return
    
    if flag == task_data['flag']:
        await update_after_validate(task_data)
        await message.answer(text=f"🤙 Верный флаг! Вам начислено {task_data['score']} очков.", 
                             reply_markup=return_to_task_kb)
        return
    
    await message.answer(text="❌ Неправильный флаг", 
                         reply_markup=return_to_task_kb)


async def update_after_validate(task_data: dict):
    users = await get_all_users(User.task_id, task_data['id'])
    for user in users:
        await update_user_by_id(user['id'], User.score, user['score'] + task_data['score'])
        if user['completed_tasks']:
            await update_user_by_id(user['id'], User.completed_tasks, user['completed_tasks'] + ',' + str(task_data['id']))
        else:
            await update_user_by_id(user['id'], User.completed_tasks, str(task_data['id']))
        await update_user_by_id(user['id'], User.task_id, -1)