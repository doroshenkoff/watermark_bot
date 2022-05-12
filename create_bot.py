import os
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from queue import LifoQueue
from aiogram.dispatcher.filters.state import State, StatesGroup
from config import *



params = {
    'vote_up': 0,
    'vote_down': 0
}

class FSMStates(StatesGroup):
    city = State()
    image_for_watermark = State()
    watermark_word = State()


storage = MemoryStorage()
bot = Bot(TOKEN_TELEGRAM)
dp = Dispatcher(bot, storage=storage)
history = LifoQueue()
