from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram import types, Dispatcher, Bot

btn_back = KeyboardButton('⏪Назад')

class KeyboardHandler:
    btn_weather = KeyboardButton('☀Погода')
    btn_currency = KeyboardButton('💱Финансы')
    btn_watermark = KeyboardButton('💧Нанести водяной знак')
    btn_inline = KeyboardButton('🌎Положение планет')

    btn_back = KeyboardButton('⏪Назад')
    btn_undo = KeyboardButton('☠Отменить')

    main_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True) \
        .add(btn_weather).add(btn_currency).add(btn_watermark).add(btn_inline)
    undo_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True).add(btn_undo)

    # ***************end of main keyboard********************************





