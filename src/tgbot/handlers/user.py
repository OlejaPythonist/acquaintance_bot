from aiogram import (  # type: ignore
    Dispatcher,
    Bot,
    types
)
from aiogram.dispatcher import FSMContext  # type: ignore
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from functools import partial
from tgbot.keyboards.user import command_kb, like_kb, gender_kb, ldr
from tgbot.FSM.states import UserProfile, Simp
from tgbot.database.requests import check_profile, ankets, user_profile
from tgbot.types_ import Profile_


async def start(message: types.Message) -> None:
    await message.answer(
        "Привет:) Это бот для знакомств, выберите команду",
        reply_markup=command_kb
    )


async def myprofile(
        session: async_sessionmaker[AsyncSession],
        message: types.Message) -> None:
    profile = await check_profile(
        session,
        message.from_user.id
    )
    if profile is None:
        await message.answer("У Вас еще нет анкеты.")
        return None
    await message.answer_photo(
        caption=f"{profile.name}, {profile.city}, {profile.age}\n\n"
                f"{profile.description}",
        photo=profile.photo
    )


async def get_ankets(
        session: async_sessionmaker[AsyncSession],
        message: types.Message,
        state: FSMContext) -> None:
    profile = await check_profile(
        session,
        message.from_user.id
    )
    if profile is None:
        await message.answer("У Вас отсутствует анкета.")
        return None
    gender = "Девушка" if profile.like == "Девушки" else "Парень"
    like = "Девушки" if profile.gender == "Девушка" else "Парни"
    anket = await ankets(
        session,
        gender,
        profile.age,
        like,
        message.from_user.id,
        profile.city
    )
    if anket is None:
        await message.answer("Нет подходящих пользователей")
        return None
    await message.answer_photo(
        caption=f"{anket[5]},{anket[4]},{anket[1]}"
                f"\n{anket[6]}\n\n/ankets",
        photo=anket[7],
        reply_markup=ldr
    )
    await Simp.id.set()
    await state.update_data(id=anket[0])
    await Simp.next()


async def cancel(_: types.Message, state: FSMContext) -> None:
    if (await state.get_state()) is None:
        return
    await state.finish()


async def edit_profile(
        message: types.Message,
        state: FSMContext) -> None:
    await UserProfile.next()
    await message.answer(
        "Сколько Вам лет?",
        reply_markup=None
    )


async def get_age(
        message: types.Message,
        state: FSMContext) -> None:
    await state.update_data(age=message.text)
    await UserProfile.gender.set()
    await message.answer(
        "Какого Вы пола?",
        reply_markup=gender_kb
    )


async def get_gender(
        message: types.Message, state: FSMContext) -> None:
    text = message.text
    if not (text in ["Парень", "Девушка"]):
        await message.answer(
            "Нет такого варианта ответа. Выберите пол."
        )
        return None
    await state.update_data(gender=message.text)
    await UserProfile.like.set()
    await message.answer(
        "Чьи анкеты Вы бы хотели посмотреть",
        reply_markup=like_kb
    )


async def get_like(
        message: types.Message,
        state: FSMContext) -> None:
    text = message.text
    if not (text in ["Парни", "Девушки"]):
        await message.answer(
            "Нет такого варианта ответа. Попробуйте еще раз"
        )
        return None
    await state.update_data(like=text)
    await UserProfile.city.set()
    await message.answer(
        "Из какого Вы города?\n"
        "(Вводите город правильно,"
        "без лишних пробелов с большой буквы."
        "Например: Москва)",
        reply_markup=None
    )


async def get_city(
        message: types.Message,
        state: FSMContext) -> None:
    await state.update_data(city=message.text)
    await UserProfile.name.set()
    await message.answer(
        "Как Вас зовут?"
    )


async def get_name(
        message: types.Message,
        state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await UserProfile.description.set()
    await message.answer(
        "Добавьте краткое описание"
    )


async def get_description(
        message: types.Message,
        state: FSMContext) -> None:
    await state.update_data(description=message.text)
    await UserProfile.photo.set()
    await message.answer(
        "Добавьте фото"
    )


async def get_photo(
        session: async_sessionmaker[AsyncSession],
        message: types.Message,
        state: FSMContext) -> None:
    id_ = message.from_user.id
    await state.update_data(photo=message.photo[0].file_id)
    await message.answer("Ваша анкета:")
    data = await state.get_data()
    await message.answer_photo(
        caption=f"{data['name']},{data['city']},{data['age']}\n\n"
                f"{data['description']}",
        photo=data['photo']
    )
    await user_profile(
        session,
        Profile_(
            id_,
            data["age"],
            data["gender"],
            data["like"],
            data["city"],
            data["name"],
            data["description"],
            data["photo"]
        )
    )
    await state.finish()


async def simp(
        session: async_sessionmaker[AsyncSession],   
        message: types.Message, 
        state: FSMContext) -> None:
    id_ = message.from_user.id
    if message.text == "👎":
        await state.finish()
        return None
    elif message.text == "👍":
        data = await state.get_data()
        profile = await check_profile(session, id_)
        if profile is None:
            await message.answer(id_, "У Вас еще нет анкеты.")
            await state.finish()
            return None
        await message.bot.send_photo(
            int(data["id"]),
            caption=f"{profile.name}, {profile.city}, {profile.age}\n\n"
                    f"{profile.description}\n\n"
                    f"@{message.from_user.username}",
            photo=profile.photo
        )
        await state.finish()
    elif message.text == "/report":
        data = await state.get_data()
        # TODO send report
        await message.answer(id_, "Жалоба была отправлена.")
        await state.finish()


def register_user(
        dp: Dispatcher,
        session: async_sessionmaker[AsyncSession]) -> None:
    dp.register_message_handler(start, commands=["start"])
    dp.register_message_handler(
        partial(myprofile, session),
        commands=["myprofile"]
    )
    dp.register_message_handler(
        partial(get_ankets, session),
        commands=["ankets"]
    )
    dp.register_message_handler(edit_profile, commands=["edit_profile"])
    dp.register_message_handler(cancel, commands=["отмена"], state="*")
    dp.register_message_handler(get_age, state=UserProfile.age)
    dp.register_message_handler(get_gender, state=UserProfile.gender)
    dp.register_message_handler(get_like, state=UserProfile.like)
    dp.register_message_handler(get_city, state=UserProfile.city)
    dp.register_message_handler(get_name, state=UserProfile.name)
    dp.register_message_handler(get_description, state=UserProfile.description)
    dp.register_message_handler(
        partial(get_photo, session),
        state=UserProfile.photo,
        content_types=[types.ContentType.PHOTO]
    )
    dp.register_message_handler(
        partial(simp, session),
        state=Simp.simp
    )
