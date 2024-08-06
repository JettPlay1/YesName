from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


# Основное меню
main_menu_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Отобразить задание", callback_data="get_task"),
                 InlineKeyboardButton(text="Рейтинг", callback_data="rating")],
                [InlineKeyboardButton(text="Магазин", callback_data="shop"),
                 InlineKeyboardButton(text="Ачивки", callback_data="achievements")]
            ]
        )

# Кнопка вернуться
return_back_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Вернуться назад", callback_data="main_menu")],
            ]
        )

# Сдать флаг
flag_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Сдать флаг", callback_data="send_flag")],
        [InlineKeyboardButton(text="Вернуться", callback_data="main_menu")]
    ]
)

# Пустая клавиатура
empty_kb = InlineKeyboardMarkup(
    inline_keyboard=[]
)