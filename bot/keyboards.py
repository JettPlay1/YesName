from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


# Основное меню
main_menu_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Получить задание", callback_data="get_task")],
                [InlineKeyboardButton(text="Получить слушателя", callback_data="get_listener")],
                [InlineKeyboardButton(text="Оставить отзыв", callback_data="leave_feedback")],
                [InlineKeyboardButton(text="Магазин", callback_data="shop")]
            ]
        )

# Кнопка вернуться
return_back_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Вернуться назад", callback_data="main_menu")],
            ]
        )