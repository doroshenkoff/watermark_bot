from .finance_keyboard import finance_kb
from .finance_utils import currency_foreign, get_nbu_cur
from aiogram import types
from aiogram.dispatcher.filters import Text
from create_bot import *
from main_keyboard import KeyboardHandler


async def finance_handler(msg: types.Message):
    history.put(KeyboardHandler.main_kb)
    await msg.reply('Выберите нужную информацию из пункта меню', reply_markup=finance_kb)


async def get_nbu(msg: types.Message):
    await msg.reply(get_nbu_cur(), reply_markup=KeyboardHandler.main_kb)


async def get_global_quotations(msg: types.Message):
    await msg.reply(currency_foreign(), reply_markup=KeyboardHandler.main_kb)


def register_handlers_finance(dp: Dispatcher):
    dp.register_message_handler(finance_handler, Text('💱Финансы'))
    dp.register_message_handler(get_nbu, Text('🏦Курсы НБУ'))
    dp.register_message_handler(get_global_quotations, Text('💹Котировки на мировой бирже'))






