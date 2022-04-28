from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram import types, Dispatcher, Bot


class KeyboardHandler:
    btn_weather = KeyboardButton('☀Погода')
    btn_weather_simple = KeyboardButton('🌡Температура воздуха')
    btn_weather_with_sun = KeyboardButton('☔🌢🌅Полная информация')
    btn_currency = KeyboardButton('💱Курсы валют')
    bt_location = KeyboardButton('Ваше расположение', request_location=True)
    btn_kiev = KeyboardButton('🌃Киев')
    btn_other_city = KeyboardButton('🏞Выберите населенный пункт')

    weather_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    location_client = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)

    kb_client.add(btn_weather).add(btn_currency)
    weather_client.add(btn_weather_simple, btn_weather_with_sun)
    location_client.row(btn_kiev, btn_other_city, bt_location)


