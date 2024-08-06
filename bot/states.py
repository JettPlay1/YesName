from aiogram.fsm.state import State, StatesGroup

class Form_send_flag(StatesGroup):
    sending = State()