from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

class InlineKeyboardHandler:
    ibtn_like = InlineKeyboardButton('👍', callback_data='like')
    ibtn_dislike = InlineKeyboardButton('👎', callback_data='dislike')

    vote_ikb = InlineKeyboardMarkup().add(ibtn_like, ibtn_dislike)