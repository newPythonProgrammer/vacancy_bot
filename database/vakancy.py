import sqlite3


class Vacancy_data_class:
    '''Класс для управления БД с вакансиями'''
    def __init__(self):
        with sqlite3.connect('vacancy.db') as connect:
            cursor = connect.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS vacancy(
            Chat_ID INTEGER,
            Message_ID INTEGER,
            Users_ID TEXT)''')

    def add_vacancy(self, chat_id, message_id, users_id):
        '''Добавляем вакансию'''
        with sqlite3.connect('vacancy.db') as connect:
            cursor = connect.cursor()
            cursor.execute('''INSERT INTO vacancy(Chat_ID, Message_ID, Users_ID) VALUES (?,?,?)''', (chat_id, message_id, users_id))

    def get_vacancy(self, user_id):
        '''получаем вакансии для какого то юзера'''
        with sqlite3.connect('vacancy.db') as connect:
            cursor = connect.cursor()
            cursor.execute(f'''SELECT Chat_id, Message_ID, Users_ID FROM vacancy WHERE Users_ID LIKE "%{user_id}%"''')
            data = cursor.fetchall()
            cursor.execute(f'''SELECT Chat_id, Message_ID FROM vacancy WHERE Users_ID LIKE "%{user_id}%"''')
            end_data = cursor.fetchall()
            if len(data) >=1:
                for chat_id, message_id, users_id in data:
                    new_users_id = users_id.replace(user_id, '')
                    if len(new_users_id.split()) == 0:
                        cursor.execute('''DELETE FROM vacancy WHERE Chat_id = ? AND Message_ID=?''', (chat_id, message_id))
                    else:
                        cursor.execute('''UPDATE vacancy SET Users_ID = ? WHERE Chat_id = ? AND Message_ID=?''', (new_users_id, chat_id, message_id))

            if len(end_data) >=1:
                return end_data
            return None


