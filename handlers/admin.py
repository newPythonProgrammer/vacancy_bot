import ast
import asyncio
from typing import List, Union

from aiogram import Dispatcher
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

import config
from database.spam import Spam_data_class
from database.user import User_data_class
from database.link import Link_data_class
from other import keyboard

User_data = User_data_class()
Links_data = Link_data_class()
Spam_data = Spam_data_class()
class FSM_ADMIN_SPAM(StatesGroup):
    text = State()
    btns = State()

class FSM_add_link(StatesGroup):
    descript = State()

class AlbumMiddleware(BaseMiddleware):
    """This middleware is for capturing media groups."""

    album_data: dict = {}

    def __init__(self, latency: Union[int, float] = 0.01):
        """
        You can provide custom latency to make sure
        albums are handled properly in highload.
        """
        self.latency = latency
        super().__init__()

    async def on_process_message(self, message: types.Message, data: dict):
        if not message.media_group_id:
            return

        try:
            self.album_data[message.media_group_id].append(message)
            raise CancelHandler()  # Tell aiogram to cancel handler for this group element
        except KeyError:
            self.album_data[message.media_group_id] = [message]
            await asyncio.sleep(self.latency)

            message.conf["is_last"] = True
            data["album"] = self.album_data[message.media_group_id]

    async def on_post_process_message(self, message: types.Message, result: dict, data: dict):
        """Clean up after handling our album."""
        if message.media_group_id and message.conf.get("is_last"):
            del self.album_data[message.media_group_id]


async def get_admin_panel(message: Message):
    user_id = message.from_user.id
    if user_id in config.ADMINS:
        name = message.from_user.first_name
        await message.answer(f'Вот твоя админ панель, {name}', reply_markup=keyboard.admin_panel())



async def stat(call: CallbackQuery):
    user_id = call.from_user.id
    if user_id in config.ADMINS:
        await call.answer()
        await call.message.answer(User_data.get_stat())

async def check_users(call: CallbackQuery, state: FSMContext):
    await state.finish()
    await call.answer()
    user_id = call.from_user.id
    if user_id in config.ADMINS:
        await call.answer()
        all_ids = User_data.get_all_user_id()
        await call.message.answer(f'Считано {len(all_ids)} пользователей запускаю проверку')
        active = 0
        not_active = 0
        for user in all_ids:
            user = int(user)
            try:
                await call.bot.send_chat_action(user, types.ChatActions.TYPING)
                active += 1
            except:
                not_active += 1
                User_data.disactive_user(user)
        await call.message.answer(f'Активных: {active}\n'
                                  f'Не активных: {not_active}')

async def spam1(call: CallbackQuery, state: FSMContext):
    await call.answer()
    await state.finish()
    user_id = call.from_user.id
    if user_id in config.ADMINS:
        await call.answer()
        await call.message.answer('Пришли пост')
        await FSM_ADMIN_SPAM.text.set()


async def spam2_media_group(message: types.Message, album: List[types.Message], state: FSMContext):
    """This handler will receive a complete album of any type."""
    media_group = types.MediaGroup()
    for obj in album:
        if obj.photo:
            file_id = obj.photo[-1].file_id
        else:
            file_id = obj[obj.content_type].file_id

        try:
            # We can also add a caption to each file by specifying `"caption": "text"`
            media_group.attach({"media": file_id, "type": obj.content_type, "caption": obj.caption,
                                "caption_entities": obj.caption_entities})
        except ValueError:
            return await message.answer("This type of album is not supported by aiogram.")
    media_group = ast.literal_eval(str(media_group))
    async with state.proxy() as data:
        try:
            data['text'] = media_group[0]['caption']
        except:
            data['text'] = 'None'
        data['media'] = media_group
        Spam_data.make_spam(data['text'], 'None', str(media_group))

    await message.answer_media_group(media_group)
    await message.answer(f'Пришли команду /sendspam_{Spam_data.select_id()} чтоб начать рассылку')
    await state.finish()


async def spam2(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in config.ADMINS:
        if message.content_type in ('photo', 'video', 'animation'):
            async with state.proxy() as data:
                try:
                    data['text'] = message.html_text
                except:
                    data['text'] = None
                if message.content_type == 'photo':
                    data['media'] = ('photo', message.photo[-1].file_id)
                else:
                    data['media'] = (message.content_type, message[message.content_type].file_id)
        else:
            async with state.proxy() as data:
                data['text'] = message.html_text
                data['media'] = 'None'
        await message.answer('Теперь пришли кнопки например\n'
                             'text - url1\n'
                             'text2 - url2 && text3 - url3\n\n'
                             'text - надпись кнопки url - ссылка\n'
                             '"-" - разделитель\n'
                             '"&&" - склеить в строку\n'
                             'ЕСЛИ НЕ НУЖНЫ КНОПКИ ОТПРАВЬ 0')
        await FSM_ADMIN_SPAM.next()


async def spam3(message: Message, state: FSMContext):
    user_id = message.from_user.id
    if user_id in config.ADMINS:
        if message.text != '0':
            # конструктор кнопок
            try:
                buttons = []
                for char in message.text.split('\n'):
                    if '&&' in char:
                        tmpl = []
                        for i in char.split('&&'):
                            tmpl.append(dict([i.split('-', maxsplit=1)]))
                        buttons.append(tmpl)
                    else:
                        buttons.append(dict([char.split('-', maxsplit=1)]))
                menu = InlineKeyboardMarkup()
                btns_list = []
                items = []
                for row in buttons:
                    if type(row) == dict:
                        url1 = str(list(row.items())[0][1]).strip()
                        text1 = list(row.items())[0][0]
                        menu.add(InlineKeyboardButton(text=text1, url=url1))
                    else:
                        items.clear()
                        btns_list.clear()
                        for d in row:
                            items.append(list(d.items())[0])
                        for text, url in items:
                            url = url.strip()
                            btns_list.append(InlineKeyboardButton(text=text, url=url))
                        menu.add(*btns_list)
                ###########$##############
                async with state.proxy() as data:
                    data['btns'] = str(menu)
                    media = data['media']
                    text = data['text']
                    Spam_data.make_spam(text, str(menu), str(media))
                    if media != 'None':
                        content_type = media[0]
                        if content_type == 'photo':
                            await message.bot.send_photo(user_id, media[1], caption=text, parse_mode='HTML',
                                                         reply_markup=menu)
                        elif content_type == 'video':
                            await message.bot.send_video(user_id, media[1], caption=text, parse_mode='HTML',
                                                         reply_markup=menu)
                        elif content_type == 'animation':
                            await message.bot.send_animation(user_id, media[1], caption=text, parse_mode='HTML',
                                                             reply_markup=menu)
                    else:
                        await message.answer(text, reply_markup=menu, parse_mode='HTML', disable_web_page_preview=True)

            except Exception as e:
                await message.reply(f'Похоже что непрвильно введена клавиатура')
        else:
            async with state.proxy() as data:
                data['btns'] = 'None'
                media = data['media']
                text = data['text']
                Spam_data.make_spam(text, 'None', str(media))

                if media != 'None':
                    content_type = media[0]
                    if content_type == 'photo':
                        await message.bot.send_photo(user_id, media[1], caption=text, parse_mode='HTML')
                    elif content_type == 'video':
                        await message.bot.send_video(user_id, media[1], caption=text, parse_mode='HTML')
                    elif content_type == 'animation':
                        await message.bot.send_animation(user_id, media[1], caption=text, parse_mode='HTML')
                else:
                    await message.answer(text, parse_mode='HTML', disable_web_page_preview=True)
        await message.answer(f'Пришли команду /sendspam_{Spam_data.select_id()} чтоб начать рассылку')
        await state.finish()


async def start_spam(message: Message, state: FSMContext):
    await state.finish()
    user_id = message.from_user.id
    if user_id in config.ADMINS:
        spam_id = int(message.text.replace('/sendspam_', ''))
        text = Spam_data.select_text(spam_id)
        keyboard = Spam_data.select_keyboard(spam_id)
        media = Spam_data.select_media(spam_id)
        if text == 'None':
            text = None
        if keyboard == 'None':
            keyboard = None
        all_user = User_data.get_all_user_id()
        await message.answer(f'Считанно {len(all_user)} пользователей запускаю рассылку')
        no_send = 0
        send = 0
        for user in all_user:
            user = int(user)
            try:
                if media != 'None' and media != None:  # Есть медиа
                    if type(media) is list:
                        await message.bot.send_media_group(user, media)
                    else:
                        content_type = media[0]

                        if content_type == 'photo':
                            await message.bot.send_photo(user, media[1], caption=text, parse_mode='HTML',
                                                         reply_markup=keyboard)
                        elif content_type == 'video':
                            await message.bot.send_video(user, media[1], caption=text, parse_mode='HTML',
                                                         reply_markup=keyboard)
                        elif content_type == 'animation':
                            await message.bot.send_animation(user, media[1], caption=text, parse_mode='HTML',
                                                             reply_markup=keyboard)

                else:  # Нету медиа
                    if keyboard != 'None' and keyboard != None:  # Есть кнопки
                        await message.bot.send_message(chat_id=user, text=text, reply_markup=keyboard,
                                                       parse_mode='HTML', disable_web_page_preview=True)
                    else:
                        await message.bot.send_message(chat_id=user, text=text, parse_mode='HTML',
                                                       disable_web_page_preview=True)
                send += 1
                User_data.active_user(user)

            except:
                no_send += 1
                User_data.disactive_user(user)
        await message.answer(f'Рассылка окончена.\n'
                             f'Отправленно: {send} пользователям\n'
                             f'Не отправленно: {no_send} пользователям')

async def add_link(call: CallbackQuery, state: FSMContext):
    await state.finish()
    user_id = call.from_user.id
    await call.answer()
    if user_id in config.ADMINS:
        await call.answer()
        await call.message.answer('Пришли мне описание ссылки')
        await FSM_add_link.descript.set()


async def add_link2(message: Message, state: FSMContext):
    user_id = message.from_user.id

    if user_id in config.ADMINS:
        Links_data.add_link(message.text)
        link = Links_data.get_all_links()[-1][0]
        link = f't.me/devseye_bot?start={link}'
        await message.answer(f'Ссылка добавленна {link}')
    await state.finish()


async def get_all_links(call: CallbackQuery, state: FSMContext):
    await state.finish()
    user_id = call.from_user.id
    if user_id in config.ADMINS:
        await call.answer()
        all_links = Links_data.get_all_links()
        if len(all_links) >0:
            for link, descript, count in all_links:
                menu = InlineKeyboardMarkup()
                btn1 = InlineKeyboardButton(text='❌Удалить❌', callback_data=f'dellink_{link}')
                menu.add(btn1)
                result_link = f't.me/devseye_bot?start={link}'
                await call.message.answer(f'Ссылка: {result_link}\n'
                                          f'Описание: {descript}\n'
                                          f'Присоединилось: {count}', reply_markup=menu)
        else:
            await call.message.answer('Ссылок нет')


async def del_link(call: CallbackQuery, state: FSMContext):
    await state.finish()
    user_id = call.from_user.id
    if user_id in config.ADMINS:
        await call.answer()
        link = call.data.split('_')[-1]
        Links_data.del_link(int(link))
        await call.bot.delete_message(user_id, call.message.message_id)
        await call.message.answer('Удалена')

def register_admin(dp: Dispatcher):
    dp.register_message_handler(get_admin_panel, commands=['panel'])
    dp.register_callback_query_handler(stat, lambda call: call.data == 'stat', state='*')

    dp.register_callback_query_handler(spam1, lambda call: call.data == 'spam', state='*')
    dp.register_callback_query_handler(check_users, lambda call: call.data=='check_users', state='*')

    dp.register_message_handler(spam2_media_group, is_media_group=True, content_types=types.ContentType.ANY,
                                state=FSM_ADMIN_SPAM.text)
    dp.register_message_handler(spam2, content_types=['photo', 'video', 'animation', 'text'], state=FSM_ADMIN_SPAM.text)
    dp.register_message_handler(spam3, state=FSM_ADMIN_SPAM.btns, content_types=['text'])
    dp.register_message_handler(start_spam, lambda message: str(message.text).startswith('/sendspam_'), state='*')
    dp.register_callback_query_handler(get_all_links, lambda call: call.data == 'get_all_links', state='*')
    dp.register_callback_query_handler(del_link, lambda call: call.data.startswith('dellink'), state='*')
    dp.register_callback_query_handler(add_link, lambda call: call.data == 'add_link', state='*')
    dp.register_message_handler(add_link2, state=FSM_add_link.descript)
