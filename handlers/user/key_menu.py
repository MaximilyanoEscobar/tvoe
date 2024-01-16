import re

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiohttp import ClientResponseError

from api.tvoe.requests import TvoeAPI
from data.keyboard import key_input_kb_text, generate_cancel_input_kb
from domain.repository.key import KeysRepository
from domain.repository.user import UsersRepository
from loader import InputUser

key_router = Router()


@key_router.message(F.text == key_input_kb_text)
async def key_press(message: Message, state: FSMContext):
    message = await message.answer(
        text='<b>🔴 Введите купленный вами ключ 🔑</b>',
        reply_markup=generate_cancel_input_kb()
    )
    await state.update_data(message=message)
    await state.set_state(InputUser.key)


@key_router.message(InputUser.key)
async def key_input(message: Message, state: FSMContext):
    key = re.search(r'[a-z0-9]{32}', message.text)
    if not key:
        return await message.reply(text='<b>🔴 Ключ неверного формата ❌</b>')
    key = key.group(0)
    state_data = await state.get_data()
    await state.clear()
    message_before: Message = state_data['message']
    await message_before.edit_reply_markup()
    keys_repo = KeysRepository()
    key_data = await keys_repo.get_key_data_by_key(key=key)
    users_repo = UsersRepository()
    user_data = await users_repo.get_user_by_tg_id(tg_id=message.from_user.id)
    if not key_data:
        return await message.reply('<b>🔴 Такой ключ отсутствует в базе ❌</b>')
    elif key_data.is_used:
        return await message.reply('<b>🔴 Ключ уже использован ❌</b>')
    elif (key_data.user_id == user_data.id) or key_data.user_id is None:
        message = await message.answer(
            text='<b>🔴 Пришлите почту, привязанную к аккаунту "ТВОЁ":</b>',
            reply_markup=generate_cancel_input_kb()
        )
        await state.update_data(message=message, id=key_data.id)
        await state.set_state(InputUser.email)
    key_data.user_id = user_data.id
    await keys_repo.update_key_data_by_id(id=key_data.id, key_data=key_data)

