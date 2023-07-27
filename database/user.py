import sqlite3
import numpy



class User_data_class:
    '''Класс для управления БД с данными юзеров'''
    def __init__(self):
        with sqlite3.connect('user.db') as connect:
            cursor = connect.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS users(
            User_ID INTEGER,
            First_Name TEXT,
            Username TEXT,
            Surname TEXT,
            Activ INTEGER DEFAULT 1,
            Key_Words TEXT,
            Kind_Work TEXT,
            Location TEXT,
            Status INTEGER DEFAULT 1)''')


    def add_user(self, user_id, first_name, username, surname):
        '''Добавляем нового пользователя'''
        with sqlite3.connect('user.db') as connect:
            cursor = connect.cursor()
            cursor.execute('''SELECT * FROM users WHERE User_ID = ?''', (user_id,))
            checker = cursor.fetchone()
            if not checker:
                cursor.execute('''INSERT INTO users(User_ID, First_Name, Username, Surname) VALUES(?,?,?,?)''',
                               (user_id, first_name, username, surname))


    def check_user_db(self, user_id) -> bool:
        with sqlite3.connect('user.db') as connect:
            cursor = connect.cursor()
            cursor.execute('''SELECT * FROM users WHERE User_ID = ?''', (user_id,))
            checker = cursor.fetchone()
            return bool(checker)


    def disactive_user(self, user_id):
        '''Устанавливаем значение что пользователь не активный'''
        with sqlite3.connect('user.db') as connect:
            cursor = connect.cursor()
            cursor.execute('''UPDATE users SET Activ = 0 WHERE User_ID = ?''', (user_id,))


    def active_user(self, user_id):
        '''Устанавливаем значение что юзер активный'''
        with sqlite3.connect('user.db') as connect:
            cursor = connect.cursor()
            cursor.execute('''UPDATE users SET Activ = 1 WHERE User_ID = ?''', (user_id,))


    def get_stat(self) -> str:
        '''Получаем статистику'''
        with sqlite3.connect('user.db') as connect:
            cursor = connect.cursor()
            cursor.execute('''SELECT count(DISTINCT User_ID) FROM users as count WHERE Activ = 1''')
            active_users = cursor.fetchone()[0]
            cursor.execute('''SELECT count(DISTINCT User_ID) FROM users as count WHERE Activ = 0''')
            disactive_users = cursor.fetchone()[0]
            cursor.execute('''SELECT count(DISTINCT User_ID) FROM users as count''')
            all_users = cursor.fetchone()[0]
            return f'Всего пользователей когда-либо запустивших бота - {all_users}\n' \
                   f'Активных пользователей - {active_users}\n' \
                   f'Неактивных пользователей - {disactive_users}'


    def get_all_user_id(self):
        '''Получаем массив всех айди юзеров'''
        with sqlite3.connect('user.db') as connect:
            cursor = connect.cursor()
            cursor.execute('''SELECT User_ID FROM users''')
            all_ids = numpy.array(cursor.fetchall()).flatten()
            return all_ids

    def get_all_user_id_status1(self):
        '''Получаем массив всех айди юзеров которые получают вакансии'''
        with sqlite3.connect('user.db') as connect:
            cursor = connect.cursor()
            cursor.execute('''SELECT User_ID FROM users WHERE Status = 1''')
            all_ids = numpy.array(cursor.fetchall()).flatten()
            return all_ids


    def set_key_words(self, user_id, words):
        '''Устанавливаем значение для ключевых слов'''
        with sqlite3.connect('user.db') as connect:
            cursor = connect.cursor()
            cursor.execute('''UPDATE users SET Key_Words = ? WHERE User_ID = ?''', (words, user_id))


    def set_kind_work(self, user_id, kind_work):
        '''Устанавливаем значение для вида работы'''
        with sqlite3.connect('user.db') as connect:
            cursor = connect.cursor()
            cursor.execute('''UPDATE users SET Kind_Work = ? WHERE User_ID = ?''', (kind_work, user_id))


    def set_location(self, user_id, location):
        '''Устанавливаем локацию работы'''
        with sqlite3.connect('user.db') as connect:
            cursor = connect.cursor()
            cursor.execute('''UPDATE users SET Location = ? WHERE User_ID = ?''', (location, user_id))


    def get_list_key_words(self, user_id) -> list:
        '''Получаем список ключевых слов'''
        with sqlite3.connect('user.db') as connect:
            cursor = connect.cursor()
            cursor.execute('''SELECT Key_Words FROM users  WHERE User_ID = ?''', (user_id,))
            result = cursor.fetchone()
            data_end = []
            if result[0] != None:
                data = result[0].split(',')
                for word in data:
                    data_end.append(word.strip())

            return data_end


    def get_key_words(self, user_id) -> str:
        '''Получаем строку ключевых слов'''
        with sqlite3.connect('user.db') as connect:
            cursor = connect.cursor()
            cursor.execute('''SELECT Key_Words FROM users  WHERE User_ID = ?''', (user_id,))
            result = cursor.fetchone()

            return result[0]


    def get_kind_work(self, user_id) -> str:
        '''Получаем список вида работы'''
        with sqlite3.connect('user.db') as connect:
            cursor = connect.cursor()
            cursor.execute('''SELECT Kind_Work FROM users  WHERE User_ID = ?''', (user_id,))
            result = cursor.fetchone()
            return result[0]


    def get_location(self, user_id) -> str:
        '''Получаем список локации'''
        with sqlite3.connect('user.db') as connect:
            cursor = connect.cursor()
            cursor.execute('''SELECT Location FROM users  WHERE User_ID = ?''', (user_id,))
            result = cursor.fetchone()
            return result[0]


    def get_ok_status_user_id(self):
        '''Получаем айди юзеров у которых статус приема заказов 1'''
        with sqlite3.connect('user.db') as connect:
            cursor = connect.cursor()
            cursor.execute('''SELECT User_ID FROM users WHERE Status = 1''')
            all_ids = numpy.array(cursor.fetchall()).flatten()
            return all_ids


    def get_profile(self, user_id) -> str:
        '''Получение профиля'''
        with sqlite3.connect('user.db') as connect:
            cursor = connect.cursor()
            cursor.execute('''SELECT Key_Words FROM users  WHERE User_ID = ?''', (user_id,))
            key_words = cursor.fetchone()
            key_words = key_words[0] #Ключевые слова
            cursor.execute('''SELECT Kind_Work FROM users  WHERE User_ID = ?''', (user_id,))
            result_kind = cursor.fetchone()
            result_kind = result_kind[0]#Вид работы
            result_kind_text = result_kind.replace('udal', 'удаленая').replace('gibrid', 'гибридная').replace('ofic', 'офисная').replace('relok', 'релокация')

            if ('gibrid' in result_kind) or ('ofic' in result_kind):
                cursor.execute('''SELECT Location FROM users  WHERE User_ID = ?''', (user_id,))
                location = cursor.fetchone()
                location = location[0]
                text = f'Специальность:  {key_words}\n\n' \
                       f'Занятость:  {result_kind_text}\n\n' \
                       f'Локация:  {location}\n\n'\
                       f'Как только мы найдем подходящие вакансии, сразу пришлем их в бот. \n' \
                       f'Для изменения параметров перейди в настройки профиля.'
            else:
                text = f'Специальность:  {key_words}\n\n' \
                       f'Занятость:  {result_kind_text}\n\n' \
                       f'Как только мы найдем подходящие вакансии, сразу пришлем их в бот. \n'\
                       f'Для изменения параметров перейди в настройки профиля.'
            return text


    def get_status(self, user_id) -> bool:
        '''Получаем статус. Принимает ли вакансии юзер или нет'''
        with sqlite3.connect('user.db') as connect:
            cursor = connect.cursor()
            cursor.execute('''SELECT Status FROM users  WHERE User_ID = ?''', (user_id,))
            status = cursor.fetchone()
            status = status[0]
            return bool(status)


    def set_status_0(self, user_id):
        '''Устанавливаем статус в 0'''
        with sqlite3.connect('user.db') as connect:
            cursor = connect.cursor()
            cursor.execute('''UPDATE users SET Status = 0 WHERE User_ID = ?''', (user_id,))


    def set_status_1(self, user_id):
        '''Устанавливаем статус в 1'''
        with sqlite3.connect('user.db') as connect:
            cursor = connect.cursor()
            cursor.execute('''UPDATE users SET Status = 1 WHERE User_ID = ?''', (user_id,))



# User = User_data_class()
# list_key_words = ['Java', ' JavaScript', ' React', ' Scala', ' Python', ' C##', ' iOS', ' Android', ' C', ' C++', ' Goland', ' Ruby', ' PHP', ' Frontend', ' Backend', ' Node js', ' Solidity', ' QA Manual', ' Data Science', ' Product Manager', ' Product Analyst', ' DevsOps', ' QA Auto', ' CTO', ' Architect', ' Design', ' UX', ' UI', ' System Analyst', ' HR', ' Recruiter', ' SMM']
# list_kind_work = (['relok', 'gibrid'], ['ofic', 'udal'], ['udal', 'relok', 'gibrid'], ['ofic',], ['udal',])
# list_loc = ['Москва', ' Санкт-Петербург', ' Екатеринбург', ' Новосибирск', ' Казань', ' Самара', ' Омск', ' Красноярск', ' Владивосток', ' Нижний Новгород', ' Хабаровск', ' Сыктывкар', ' Калининград', ' Сочи', ' Астрахань', ' Челябинск', ' Чикаго', ' Нью-Йорк', ' Лос-Анджелес', ' Сан-Франциско', ' Торонто', ' Ванкувер', ' Лондон', ' Париж', ' Берлин', ' Мадрид', ' Рим', ' Амстердам', ' Вена', ' Прага', ' Варшава', ' Стокгольм', ' Киев', ' Минск', ' Тбилиси', ' Баку', ' Иерусалим', ' Астана', ' Анкара', ' Афины']
#
# for i in range(50):
#     user_id = i
#     User.add_user(user_id, 'test', 'test', 'test')
#     User.set_key_words(user_id, ", ".join([random.choice(list_key_words), random.choice(list_key_words), random.choice(list_key_words), random.choice(list_key_words)]).lower())
#     kind_work = ', '.join(random.choice(list_kind_work))
#     User.set_kind_work(user_id, kind_work)
#     if ('gibrid' in kind_work) or ('ofic' in kind_work):
#         User.set_location(user_id, ', '.join([random.choice(list_loc), random.choice(list_loc), random.choice(list_loc), random.choice(list_loc)] ))
