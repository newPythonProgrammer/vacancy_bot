from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup



def admin_panel():
    menu = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton(text='Рассылка', callback_data='spam')
    btn2 = InlineKeyboardButton(text='Статистика', callback_data='stat')
    btn3 = InlineKeyboardButton(text='Проверить всех юзеров',callback_data='check_users')
    btn4 = InlineKeyboardButton(text='Получить все приг.ссылки', callback_data='get_all_links')
    btn5 = InlineKeyboardButton(text='Добавить пригласительную ссылку', callback_data='add_link')
    menu.add(btn1, btn2, btn3 ,btn4, btn5)
    return menu



def start_btn():
    menu = InlineKeyboardMarkup()
    btn1 = InlineKeyboardButton(text='Начать настройку', callback_data='start_reg')
    menu.add(btn1)
    return menu

def kind_work_btn(user_list):
    menu = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton(text='Удаленная работа', callback_data='udal') if 'udal' not in user_list else  InlineKeyboardButton(text='✅Удаленная работа', callback_data='udal')
    btn2 = InlineKeyboardButton(text='Гибрид', callback_data='gibrid') if 'gibrid' not in user_list else InlineKeyboardButton(text='✅Гибрид', callback_data='gibrid')
    btn3 = InlineKeyboardButton(text='Релокация', callback_data='relok') if 'relok' not in user_list else InlineKeyboardButton(text='✅Релокация', callback_data='relok')
    btn4 = InlineKeyboardButton(text='Офис', callback_data='ofic') if 'ofic' not in user_list else InlineKeyboardButton(text='✅Офис', callback_data='ofic')
    btn5 = InlineKeyboardButton(text='Далее', callback_data='next')
    menu.add(btn1, btn2, btn3, btn4)
    if len(user_list) >0:
        menu.add(btn5)
    return menu


def chanel_btn_reg():
    menu = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton(text='Python Job', url='https://t.me/job_python')
    btn2 = InlineKeyboardButton(text='Java Job', url='https://t.me/job_javadevs')
    btn3 = InlineKeyboardButton(text='React Job', url='https://t.me/job_react')
    btn4 = InlineKeyboardButton(text='Web 3.0 Job', url='https://t.me/job_web3')
    btn5 = InlineKeyboardButton(text='IT Jobs', url='https://t.me/devs_it')
    btn6 = InlineKeyboardButton(text='IT Jobs (No Code)', url='https://t.me/itjobs_nocode')
    btn7 = InlineKeyboardButton(text='JavaScript Job ', url='https://t.me/JScript_jobs')
    btn_check = InlineKeyboardButton(text='Я подписался', callback_data='check_reg_sub')
    menu.add(btn1, btn2,btn7, btn3, btn4, btn5, btn6, btn_check)
    return menu

def chanel_btn_vac():
    menu = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton(text='Python Job', url='https://t.me/job_python')
    btn2 = InlineKeyboardButton(text='Java Job', url='https://t.me/job_javadevs')
    btn3 = InlineKeyboardButton(text='React Job', url='https://t.me/job_react')
    btn4 = InlineKeyboardButton(text='Web 3.0 Job', url='https://t.me/job_web3')
    btn5 = InlineKeyboardButton(text='IT Jobs', url='https://t.me/devs_it')
    btn6 = InlineKeyboardButton(text='IT Jobs (No Code)', url='https://t.me/itjobs_nocode')
    btn7 = InlineKeyboardButton(text='JavaScript Job ', url='https://t.me/JScript_jobs')
    btn_check = InlineKeyboardButton(text='Я подписался', callback_data='check_vac_sub')
    menu.add(btn1, btn2,btn7, btn3, btn4, btn5, btn6, btn_check)
    return menu


def done_btn():
    menu = InlineKeyboardMarkup()
    btn = InlineKeyboardButton(text='Перейти в главное меню', callback_data='main_menu')
    menu.add(btn)
    return menu

def menu_btn(status):
    menu = InlineKeyboardMarkup(row_width=1)
    btn1 = InlineKeyboardButton(text='Настройка профиля', callback_data='start_reg')
    btn2 = InlineKeyboardButton(text='Остановить получение ваканисй', callback_data='stop_order') if status else InlineKeyboardButton(text='Начать получение вакансий', callback_data='start_order')
    btn3 = InlineKeyboardButton(text='Поддержка', callback_data='help')
    menu.add(btn1, btn2, btn3)
    return menu