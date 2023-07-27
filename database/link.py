import sqlite3

class Link_data_class():
    '''Класс для управления БД с пригласительными ссылками'''
    def __init__(self):
        with sqlite3.connect('link.db') as connect:
            cursor = connect.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS link(
            ID INTEGER PRIMARY KEY,
            Descript TEXT,
            Count INTEGER DEFAULT 0)''')

    def add_link(self, descript):
        '''Добавляем ссылку'''
        with sqlite3.connect('link.db') as connect:
            cursor = connect.cursor()
            cursor.execute('''INSERT INTO link(Descript) VALUES(?)''', (descript,))

    def get_all_links(self):
        '''Получаем все ссылки'''
        with sqlite3.connect('link.db') as connect:
            cursor = connect.cursor()
            cursor.execute('''SELECT * FROM link''')
            result = cursor.fetchall()
            return result
    def del_link(self, link):
        '''Удалить ссылку'''
        with sqlite3.connect('link.db') as connect:
            cursor = connect.cursor()
            cursor.execute('''DELETE FROM link WHERE ID = ?''', (link,))

    def add_count(self, link):
        '''Прибавляем счетчик людей'''
        with sqlite3.connect('link.db') as connect:
            cursor = connect.cursor()
            cursor.execute('''UPDATE link SET Count = Count + 1 WHERE ID = ?''', (link,))