from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from main_keyboard import btn_back

finance_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)\
    .add(KeyboardButton('🏦Курсы НБУ'), KeyboardButton('💹Котировки на мировой бирже')).row(btn_back)