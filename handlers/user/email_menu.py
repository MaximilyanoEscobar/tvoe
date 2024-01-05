import asyncio
import re

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiohttp import ClientResponseError

from api.mts.requests import TvoeAPI
from domain.repository.key import KeysRepository
from loader import InputUser

number_router = Router()


@number_router.message(InputUser.test_email)
@number_router.message(InputUser.email)
async def input_email(message: Message, state: FSMContext):
    state_data = await state.get_data()
    state_info = await state.get_state()
    message_before: Message = state_data['message']
    search = re.match(r'([a-zA-Z0-9._-]+@[a-zA-Z0-9._-]+\.[a-zA-Z0-9_-]+)', message.text)
    if not search:
        return await message.reply('<b>🔴 Введите правильно почту:\n'
                                   'Пример: <code>test@gmail.com</code></b>')

    async def test_email() -> bool:
        keys_repo = KeysRepository()
        key_data = await keys_repo.get_key_data_by_email(email=email)
        if key_data:
            await message.reply('<b>🔴 На данную почту уже происходила накрутка баллов</b>')
            return False
        else:
            await message.reply('<b>🔴 Почта подходит! ✅</b>')
            return True

    async def real_email():
        await message.reply(text='<b>🔴 Начинается накрутка баллов</b>')
        key_id = state_data['id']
        keys_repo = KeysRepository()
        key_data = await keys_repo.get_key_data_by_id(id=key_id)
        tvoe_api = TvoeAPI()
        if key_data.is_used:
            return await message.reply('<b>🔴 Ключ уже был использован ❌</b>')
        try:
            for result_in_wheel in range(1, 11):
                await tvoe_api.create_integration(email=email,
                                                  result_in_wheel=result_in_wheel)
                await asyncio.sleep(5)

            key_data.is_used = True
            key_data.email = email
            await keys_repo.update_key_data_by_id(id=key_data.id, key_data=key_data)
            return await message.reply(text='<b>🔴 Баллы успешно накручены! ✅</b>')

        except ClientResponseError as e:
            await message.reply(
                '<b>🔴 Произошла ошибка во время накрутки баллов, обратитесь к техническому специалисту ❌</b>')

    await message_before.edit_reply_markup()
    await state.clear()
    email = search.group(0)
    if state_info.endswith('test_email'):
        return await test_email()

    elif state_info.endswith('email'):
        if await test_email():
            return await real_email()
