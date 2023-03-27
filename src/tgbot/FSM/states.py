from aiogram.dispatcher.filters.state import (  # type: ignore
    State,
    StatesGroup
)


class Simp(StatesGroup):  # type: ignore
    id = State()
    simp = State()


class UserProfile(StatesGroup):  # type: ignore
    age = State()
    gender = State()
    like = State()
    city = State()
    name = State()
    description = State()
    photo = State()
