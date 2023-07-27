from database.user import User_data_class

User_data = User_data_class()

data_key_words = {'python': ('питон',),
                  'битрикс': ('bitrix',),
                  'linux': ('линукс',),
                  'javascript': ('js',),
                  'typescript': ('ts',),
                  'kotlin': ('android',),
                  'swift': ('ios', 'mac',),
                  'assembly': ('ассемблер', 'асемблер'),
                  'backend': ('бекэнд', 'бэкенд', 'back-end'),
                  'frontend': ('front-end', 'фронт', 'фронтэнд', 'фронтенд'),
                  'ML': ('Machine Learning',)}


def send_vacancy(text: str):
    text = text.lower()  # приводим весь текст в нижний регистр
    text = text.replace('офис', 'ofic').replace('релок', 'relok').replace('гибрид', 'gibrid').replace('удаленка',
                                                                                                      'udal').replace(
        'удалёнка', 'udal').replace('санкт-петербург', 'питер')
    for key in data_key_words.keys():  # заменяем синонимы ключевых слов на норм слова типо питон на python
        for word in data_key_words[key]:
            text = text.replace(word, key)
    all_user_id = User_data.get_all_user_id_status1() #Получаем юзеров у которых статус приема вакансий 1

    # Сначала находим юзеров у которых совпадает ключевые слова
    user_key_words_list = []  # Айди юзеров у которых совпали ключевые слова
    for user in all_user_id:
        user = int(user)
        check_key_words = False
        key_words = User_data.get_key_words(user)
        if key_words == None or len(key_words) < 1:
            continue
        for key in data_key_words.keys():  # заменяем синонимы ключевых слов на норм слова типо питон на python
            for word in data_key_words[key]:
                key_words = key_words.replace(word, key)

        for word in key_words.lower().split(','):
            word = word.strip()  # Убираем лишние пробелы
            if word in text:
                #print(word, user, key_words)
                check_key_words = True
                break
        if not check_key_words:  # Если ключевые слова не совпали у юзера и текста
            continue  # Переходим к следующему юзеру
        user_key_words_list.append(user)


    if len(user_key_words_list) > 1:
        user_resut = []  # Отвеиваем по виду работы и городам
        for user in user_key_words_list:
            user = user
            kind_work = User_data.get_kind_work(user)
            if kind_work == None or len(kind_work) < 1:
                continue
            kind_work = kind_work.split(',')
            for kind in kind_work:
                kind = kind.strip()  # Убираем лишние пробелы
                if kind in text:
                    if (kind == 'relok') or (kind == 'udal'):
                        user_resut.append(user)
                    else:
                        location_user = User_data.get_location(user)
                        if (location_user != None):
                            if (len(location_user) > 1):
                                location_user = location_user.lower().replace('санкт-петербург', 'питер').split(',')
                                for location in location_user:
                                    location = location.strip()  # Убираем лишние пробелы
                                    if location in text:
                                        user_resut.append(user)

        return list(set(user_resut))
    return []
