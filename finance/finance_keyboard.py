from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from main_keyboard import btn_back

finance_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)\
    .add(KeyboardButton('🏦Курсы НБУ'), KeyboardButton('💹Котировки на мировой бирже')).row(btn_back)


world_cur_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)\
    .add(KeyboardButton('💰Текущие котировки'), KeyboardButton('📈Динамика котировок')).row(btn_back)


period_kb = InlineKeyboardMarkup(resize_keyboard=True, row_width=1).add(
    InlineKeyboardButton('Текущие', callback_data='10'),
    InlineKeyboardButton('3 дня', callback_data='30'),
    InlineKeyboardButton('7 дней', callback_data='70'),
    InlineKeyboardButton('10 дней', callback_data='100'),
    InlineKeyboardButton('30 дней', callback_data='300')
)