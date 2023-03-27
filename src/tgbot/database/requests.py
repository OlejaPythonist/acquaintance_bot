from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from tgbot.database.models import Profile
from tgbot.types_ import Profile_
import random


async def check_profile(
        session: async_sessionmaker[AsyncSession],
        id: int | str) -> Profile_ | None:
    stmt = select(Profile).where(Profile.user_id == id)
    profile = None
    async with session() as sess:
        for row in await sess.execute(stmt):
            user_info = row[0]
            profile = Profile_(
                user_info.user_id,
                user_info.age,
                user_info.gender,
                user_info.like,
                user_info.city,
                user_info.name,
                user_info.description,
                user_info.photo,
            )

    return profile


async def user_profile(
        session: async_sessionmaker[AsyncSession],
        profile: Profile_) -> None:
    stmt = update(Profile).where(
        Profile.user_id == profile.user_id
    ).values(
        age=profile.age,
        gender=profile.gender,
        like=profile.like,
        city=profile.city,
        name=profile.name,
        description=profile.description,
        photo=profile.photo
    )
    async with session() as sess:
        if await check_profile(session, profile.user_id):
            await sess.execute(stmt)
        else:
            sess.add(Profile(
                 user_id=profile.user_id,
                 age=profile.age,
                 gender=profile.gender,
                 like=profile.like,
                 city=profile.city,
                 name=profile.name,
                 description=profile.description,
                 photo=profile.photo
            ))
        await sess.commit()


async def ankets(
        session: async_sessionmaker[AsyncSession],
        gender: str,
        age: int,
        like: str,
        id_: str,
        city: str) -> list[str | int] | None:
    stmt = select(Profile).where(
        Profile.user_id != id_,
        Profile.age == age,
        Profile.gender == gender,
        Profile.like == like,
        Profile.city == city
    )
    profiles = []
    async with session() as sess:
        for row in await sess.execute(stmt):
            profile = row[0]
            profiles.append([
                profile.user_id,
                profile.age,
                profile.gender,
                profile.like,
                profile.city,
                profile.name,
                profile.description,
                profile.photo
            ])
    if len(profiles) == 1:
        return profiles[0]
    elif len(profiles) > 1:
        return random.choice(profiles)
    else:
        return None
