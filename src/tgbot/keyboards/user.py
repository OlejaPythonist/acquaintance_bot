from aiogram.types import (  # type: ignore
    ReplyKeyboardMarkup,
    KeyboardButton
)
button_cancel = KeyboardButton(text="/отмена")


button_male = KeyboardButton(text="Парень")
button_female = KeyboardButton(text="Девушка")
gender_kb = ReplyKeyboardMarkup(
    keyboard=[
        [button_male, button_female],
        [button_cancel]
    ],
    resize_keyboard=True
)


button_guys = KeyboardButton(text="Парни")
button_girls = KeyboardButton(text="Девушки")
like_kb = ReplyKeyboardMarkup(
    keyboard=[
        [button_guys, button_girls],
        [button_cancel]
    ],
    resize_keyboard=True
)


button_like = KeyboardButton(text="👎")
button_dlike = KeyboardButton(text="👍")
button_report = KeyboardButton(text="/report")
ldr = ReplyKeyboardMarkup(
    keyboard=[
        [button_like, button_dlike],
        [button_report]
    ],
    resize_keyboard=True
)


button_edit_profile = KeyboardButton(text="/edit_profile")
button_myprofile = KeyboardButton(text="/myprofile")
button_start = KeyboardButton(text="/start")
button_ankets = KeyboardButton(text="/ankets")
command_kb = ReplyKeyboardMarkup(
    keyboard=[
        [button_edit_profile, button_myprofile],
        [button_ankets, button_start],
        [button_cancel]
    ],
    resize_keyboard=True
)
