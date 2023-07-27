from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

import config
from database.user import User_data_class
from database.link import Link_data_class
from database.vakancy import Vacancy_data_class
from other import keyboard, func

User_data = User_data_class()
Links_data = Link_data_class()
Vacancy_data = Vacancy_data_class()

DICT_KIND_WORK_USER = {}


class FSM_REG_USER(StatesGroup):
    key_words = State()
    kind_work = State()
    location = State()

async def new_msg(message: Message):
    '''Тут реагируем на новый пост в канале'''
    text = message.text.lower()
    if ('требования' in text) or ('задачи' in text) or ('локация' in text) or ('будет плюсом' in text)\
        or ('откликнуться' in text):
        user_id_get_vakancy = func.send_vacancy(text)

        user_id_add_vacancy = []

        for user_id in user_id_get_vakancy:
            #Проверяем подписку
            member_data = []
            for chanel in config.CHANEL_LIST:
                member = await message.bot.get_chat_member(chanel, user_id)
                if member.status == 'creator' or member.status == 'member' or member.status == 'administrator':
                    member_data.append(True)
                else:
                    member_data.append(False)

            result = any(member_data)

            #
            if result:
                try:
                    await message.bot.send_message(user_id, 'Мы нашли для тебя новую вакансию.')
                    await message.bot.forward_message(user_id, message.chat.id, message.message_id)
                except:
                   pass
            else:
                user_id_add_vacancy.append(str(user_id))
                await message.bot.send_message(user_id,
                                               'Мы нашли для тебя новую вакансию, но заметили что ты отписался от канала. Подпишись и мы отправим тебе вакансию', reply_markup=keyboard.chanel_btn_vac())

        Vacancy_data.add_vacancy(message.chat.id, message.message_id, ' '.join(user_id_add_vacancy))
async def start(message: Message):
    '''Пользователь нажал старт'''
    user_id = message.from_user.id
    name = message.from_user.first_name
    surname = message.from_user.last_name
    username = message.from_user.username
    if not User_data.check_user_db(user_id):
        if len(message.text.split()) > 1:# Если юзер присоединился по пригласительной ссылке
            link = message.text.split()[1]
            Links_data.add_count(int(link))

    User_data.add_user(user_id, name, username, surname)
    if User_data.get_key_words(user_id) != None: #Если юзер уже заполнин профиль
        status = User_data.get_status(user_id)  # Статус приема вакансий True - принимает или False не принимает
        text = 'Ваш профиль активный, вы получаете вакансии' if status else 'Ваш профиль неактивный, вы не получаете вакансии'
        await message.answer(text=text, reply_markup=keyboard.menu_btn(status))

    else:#Если не заполнил (присоединился только)
        await message.answer('''DEVSEYE – бот, в котором вы найдете работу в IT.
Подходит для разработчиков, менеджеров, управленцев и всех, чья работа связана с информационными технологиями.
    
Пройдите небольшую регистрацию, чтобы получать отобранные вакансии персонально под ваши умения.''',
                             reply_markup=keyboard.start_btn())


async def registration_1(call: CallbackQuery, state: FSMContext):
    '''Пользователь ввводит данные'''
    user_id = call.from_user.id
    await call.answer()
    await state.finish()
    await call.bot.delete_message(user_id, call.message.message_id)
    await call.message.answer('''Укажите через запятую специальности, по которым вы хотите получать вакансии.
Используй эти или добавь свои: 
Java, JavaScript, React, Scala, Python, C##, iOS, Android, C, C++, Goland, Ruby, PHP, Frontend, Backend, Node js, Solidity, QA Manual, Data Science, Product Manager, Product Analyst, DevsOps, QA Auto, CTO, Architect, Design, UX, UI, System Analyst, HR, Recruiter, SMM 

Рекомендуем использовать разные варианты написания, например:
JS, JavaScript 
Product Manager, Продакт, менеджер по продукту 

Вы будете получать вакансии, текст которых содержит указанные специальности.''')
    await FSM_REG_USER.key_words.set()


async def registration_2(message: Message, state: FSMContext):
    '''Записываем ключевые слова'''
    user_id = message.from_user.id
    async with state.proxy() as data:
        data['key_words'] = message.text
    DICT_KIND_WORK_USER[user_id] = []
    await message.answer(text='Какой тип занятости рассматриваешь?\n'\
                              'Можно выбрать один или несколько вариантов',
                         reply_markup=keyboard.kind_work_btn(DICT_KIND_WORK_USER[user_id]))
    await FSM_REG_USER.next()


async def registration_3(call: CallbackQuery, state: FSMContext):
    '''Записываем тип занятости'''
    user_id = call.from_user.id
    await call.answer()
    if call.data != 'next':
        if call.data not in DICT_KIND_WORK_USER[user_id]:
            DICT_KIND_WORK_USER[user_id].append(call.data)
        else:
            DICT_KIND_WORK_USER[user_id].remove(call.data)
        async with state.proxy() as data:
            data['kind_work'] = DICT_KIND_WORK_USER[user_id]
        await call.bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id,
                                         text='Какой тип занятости рассматриваешь?\n'
                                              'Можно выбрать один или несколько вариантов',
                                         reply_markup=keyboard.kind_work_btn(DICT_KIND_WORK_USER[user_id]))

    else:
        if ('gibrid' in DICT_KIND_WORK_USER[user_id]) or ('ofic' in DICT_KIND_WORK_USER[user_id]):
            await call.bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id,
                                             text='Перечисли пришли через запятую города, в которых тебе интересно '
                                                  'работать в офисе или гибридно:\n'
                                                  'Например: Москва, Екатеринбург, Кипр, Берлин, Санкт-Петербург',
                                             reply_markup=None)
            await FSM_REG_USER.next()
        else:
            ###Проверяем подписку
            member_data = []
            for chanel in config.CHANEL_LIST:
                member = await call.bot.get_chat_member(chanel, user_id)
                if member.status == 'creator' or member.status == 'member' or member.status == 'administrator':
                    member_data.append(True)
                else:
                    member_data.append(False)

            result = any(member_data)

            async with state.proxy() as data:
                User_data.set_kind_work(user_id, ', '.join(data['kind_work']))
                User_data.set_key_words(user_id, data['key_words'])

            if result:
                await call.message.answer(
                    f'Поздравляю, настройка завершена, теперь ты будешь получать вакансии по этим параметрам:\n\n'
                    f'{User_data.get_profile(user_id)}', reply_markup=keyboard.done_btn())
            else:
                await call.bot.edit_message_text(
                    text='Чтобы получать вакансии, подпишись на один из каналов, который тебе интересен:',
                    reply_markup=keyboard.chanel_btn_reg(), chat_id=user_id, message_id=call.message.message_id)
            await state.finish()


async def registration_4(message: Message, state: FSMContext):
    '''Записываем города'''

    user_id = message.from_user.id
    async with state.proxy() as data:
        data['location'] = message.text

    ###Проверяем подписку
    member_data = []
    for chanel in config.CHANEL_LIST:
        member = await message.bot.get_chat_member(chanel, user_id)
        if member.status == 'creator' or member.status == 'member' or member.status == 'administrator':
            member_data.append(True)
        else:
            member_data.append(False)

    result = any(member_data)

    async with state.proxy() as data:
        User_data.set_kind_work(user_id, ', '.join(data['kind_work']))
        User_data.set_key_words(user_id, data['key_words'])
        User_data.set_location(user_id, data['location'])

    if result:
        await message.answer(
            f'Поздравляю, настройка завершена, теперь ты будешь получать вакансии по этим параметрам:\n\n'
            f'{User_data.get_profile(user_id)}', reply_markup=keyboard.done_btn())
    else:
        await message.answer('Чтобы получать вакансии, подпишись на один из каналов, который тебе интересен:',
                             reply_markup=keyboard.chanel_btn_reg())
    await state.finish()


async def check_reg_sub(call: CallbackQuery):
    '''Проверяем подписку когда юзер закончил настраивать профиль'''
    user_id = call.from_user.id
    ###Проверяем подписку
    member_data = []
    for chanel in config.CHANEL_LIST:
        member = await call.bot.get_chat_member(chanel, user_id)
        if member.status == 'creator' or member.status == 'member' or member.status == 'administrator':
            member_data.append(True)
        else:
            member_data.append(False)

    result = any(member_data)

    if result:
        await call.bot.edit_message_text(
            text=f'Поздравляю, настройка завершена, теперь ты будешь получать вакансии по этим параметрам:\n\n'
                 f'{User_data.get_profile(user_id)}', chat_id=user_id, message_id=call.message.message_id,
            reply_markup=keyboard.done_btn())
    else:
        await call.answer('Ты не подписался', show_alert=True)


async def check_vac_sub(call: CallbackQuery):
    '''Проверяем подписку когда юзеру пришла вакансия и он нажал чекнуить подписку'''
    user_id = call.from_user.id

    ###Проверяем подписку
    member_data = []
    for chanel in config.CHANEL_LIST:
        member = await call.bot.get_chat_member(chanel, user_id)
        if member.status == 'creator' or member.status == 'member' or member.status == 'administrator':
            member_data.append(True)
        else:
            member_data.append(False)

    result = any(member_data)

    if result:
        await call.bot.delete_message(user_id, call.message.message_id)
        data_vacancy = Vacancy_data.get_vacancy(str(user_id))
        if data_vacancy != None:
            for chat_id, message_id in data_vacancy:
                await call.bot.forward_message(user_id, chat_id, message_id)
    else:
        await call.answer('Ты не подписался', show_alert=True)


async def main_btn(call: CallbackQuery):
    '''Главное меню когда юзер нажимает кнопку Перейти в галвное меню после настройки про'''
    user_id = call.from_user.id
    await call.answer()
    status = User_data.get_status(user_id)  # Статус приема вакансий True - принимает или False не принимает
    text = 'Ваш профиль активный, вы получаете вакансии' if status else 'Ваш профиль неактивный, вы не получаете вакансии'
    await call.bot.edit_message_text(text=text, reply_markup=keyboard.menu_btn(status), chat_id=user_id,
                                     message_id=call.message.message_id)


async def stop_order(call: CallbackQuery):
    '''Останавливаем прием заказов'''
    user_id = call.from_user.id
    await call.answer()
    User_data.set_status_0(user_id) #Устанавливаем статус в 0
    status = User_data.get_status(user_id)  # Статус приема вакансий True - принимает или False не принимает
    text = 'Ваш профиль активный, вы получаете вакансии' if status else 'Ваш профиль неактивный, вы не получаете вакансии'
    await call.bot.edit_message_text(text=text, reply_markup=keyboard.menu_btn(status), chat_id=user_id,
                                     message_id=call.message.message_id)

async def start_order(call: CallbackQuery):
    '''Возобновляем прием заказов'''
    user_id = call.from_user.id
    await call.answer()
    User_data.set_status_1(user_id) #Устанавливаем статус в 1
    status = User_data.get_status(user_id)  # Статус приема вакансий True - принимает или False не принимает
    text = 'Ваш профиль активный, вы получаете вакансии' if status else 'Ваш профиль неактивный, вы не получаете вакансии'
    await call.bot.edit_message_text(text=text, reply_markup=keyboard.menu_btn(status), chat_id=user_id,
                                     message_id=call.message.message_id)

async def get_help(call: CallbackQuery):
    '''Поддержка'''
    await call.answer()
    await call.bot.edit_message_text(text='По любым вопросам пишите: @egormk', chat_id=call.from_user.id, message_id=call.message.message_id, reply_markup=keyboard.done_btn())

def register_client(dp: Dispatcher):
    dp.register_message_handler(start, commands='start', state='*')
    dp.register_callback_query_handler(registration_1, lambda call: call.data == 'start_reg')
    dp.register_message_handler(registration_2, state=FSM_REG_USER.key_words)
    dp.register_callback_query_handler(registration_3,
                                       lambda call: call.data in ('udal', 'gibrid', 'relok', 'ofic', 'next'),
                                       state=FSM_REG_USER.kind_work)
    dp.register_message_handler(registration_4, state=FSM_REG_USER.location)
    dp.register_callback_query_handler(check_reg_sub, lambda call: call.data == 'check_reg_sub', state='*')
    dp.register_callback_query_handler(check_vac_sub, lambda call: call.data == 'check_vac_sub', state='*')
    dp.register_callback_query_handler(main_btn, lambda call: call.data == 'main_menu', state='*')
    dp.register_callback_query_handler(start_order, lambda call: call.data == 'start_order', state='*')
    dp.register_callback_query_handler(stop_order, lambda call: call.data == 'stop_order', state='*')
    dp.register_callback_query_handler(get_help, lambda call: call.data == 'help', state='*')

    dp.register_channel_post_handler(new_msg)
