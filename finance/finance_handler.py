from .finance_keyboard import finance_kb, world_cur_kb, period_kb
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
    history.put(finance_kb)
    await msg.reply("Выберите тип отображения", reply_markup=world_cur_kb)


async def get_current_quotations(msg: types.Message):
    await msg.reply(currency_foreign(), reply_markup=KeyboardHandler.main_kb)


async def get_quotation_history(msg: types.Message):
    await msg.reply('В процессе разработки', reply_markup=period_kb)


async def select_period(callback: types.CallbackQuery):
    await callback.answer()
    answer = callback.data
    if answer == '10':
        await bot.send_message(callback.from_user.id, currency_foreign(True), parse_mode='HTML')


def register_handlers_finance(dp: Dispatcher):
    dp.register_message_handler(finance_handler, Text('💱Финансы'))
    dp.register_message_handler(get_nbu, Text('🏦Курсы НБУ'))
    dp.register_message_handler(get_global_quotations, Text('💹Котировки на мировой бирже'))
    dp.register_message_handler(get_current_quotations, Text('💰Текущие котировки'))
    dp.register_message_handler(get_quotation_history, Text('📈Динамика котировок'))
    dp.register_callback_query_handler(select_period, lambda msg: msg.data in ('10', '30', '70', '100', '300'))






