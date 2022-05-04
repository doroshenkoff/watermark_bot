from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram import types, Dispatcher, Bot


class KeyboardHandler:
    # btn_start = KeyboardButton('Start')

    btn_weather = KeyboardButton('☀Погода')
    btn_currency = KeyboardButton('💱Курсы валют')
    btn_watermark = KeyboardButton('💧Нанести водяной знак')
    btn_inline = KeyboardButton('Inline button test')

    btn_weather_simple = KeyboardButton('🌡Температура воздуха')
    btn_weather_with_sun = KeyboardButton('☔🌢🌅Полная информация')
    btn_back = KeyboardButton('⏪Назад')

    btn_undo = KeyboardButton('☠Отменить')

    bt_location = KeyboardButton('Ваше расположение', request_location=True)
    btn_kiev = KeyboardButton('🌃Киев')
    btn_other_city = KeyboardButton('🏞Выберите населенный пункт')

    weather_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    weather_prognosus = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)\
        .add(KeyboardButton('⌚Текущая')).add(KeyboardButton('👀Прогноз погоды')).add(btn_back)
    kb_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    location_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    undo_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    # start_kb = ReplyKeyboardMarkup()
    # start_kb.add(btn_start)

    kb_client.add(btn_weather).add(btn_currency).add(btn_watermark).add(btn_inline)
    weather_client.add(btn_weather_simple, btn_weather_with_sun, btn_back)
    location_client.add(btn_kiev, btn_other_city, bt_location, btn_back)
    undo_client.add(btn_undo)


