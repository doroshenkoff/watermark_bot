from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class RadioInlineKeyboardButton(InlineKeyboardButton):
    def __init__(self, text, **kwargs):
        super().__init__(f'🔾  {text}', **kwargs)
        self.selected = False

    @property
    def selected(self):
        return self.selected

    @selected.setter
    def selected(self, variant):
        if variant in [True, False]:
            self.selected = variant

    def select(self):
        self.selected = True
        self.text.replace('🔘', '🔾')

    def unselect(self):
        self.selected = False
        self.text.replace('🔾', '🔘')


class RadioInlineKeyboardMarkup(InlineKeyboardMarkup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
