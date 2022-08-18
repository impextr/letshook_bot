import json


def fill_data(file_name):
    __doc__ = "Заполняет словари в зависимости от имени файла"
    d = {}
    if file_name == 'tokens':
        d = {'main': '5113148614:AAEUyd_NXuXNiluE4DR1sWBzFxrq0ag62XU',
             'test': '5264995165:AAFp6Zo3mYdiXT3kBA1eO5sc55vCWQokMrc'}
    elif file_name == 'options':
        full_rights_isers_list = ["405329215", "726466701", "354687501"]
        text = "📍Доброго вечора, ми з України ;)\n" \
               "Я чат-бот мережі кальян-барів Mr.White,\n" \
               "в мене ти можеш дізнатись все про мережу, " \
               "від меню, паролю на вайфай і бронювання столику до акцій та майбутніх вечірок!"
        text2 = 'На якому березі Києва тобі ближче?'
        d = {'Токен API Telegram': '5113148614:AAEUyd_NXuXNiluE4DR1sWBzFxrq0ag62XU',
             'Общее приветствие 1': text,
             'Общее приветствие 2': text2,
             'Имя файла общей заставки': 'White.jpg',
             'Список получателей сообщения о резерве': full_rights_isers_list,
             'Список получателей сообщения о жалобе': full_rights_isers_list,
             'Список администраторов': full_rights_isers_list,
             'Вести лог-файл': 0}
    elif file_name == 'заведения':
        net_list = []

        text = """Вітаю тебе в "Першому" на Русанівському бульварі!
            Це перший заклад мережі, з нього почалася наша кальянна історія.
            Що саме тебе цікавить?"""
        url = 'https://mrwhite1.orty.io/'
        url1 = 'https://www.google.com/maps/dir//%D0%9A%D0%B0%D0%BB%D1%8C%D1%8F%D0%BD-%D0%B1%D0%B0%D1%80+Mr.White/' \
               'data=!4m6!4m5!1m1!4e2!1m2!1m1!1s0x40d4cf8be4aa83af:0xac210e508ab17786?sa=X&ved=2ahUKEwihoKuyxar3AhVry' \
               'oUKHbSBCYMQ9Rd6BAhLEAQ'
        url2 = 'https://www.google.com/maps/place//data=!4m3!3m2!1s0x40d4cf8be4aa83af:0xac210e508ab17786!12e1?source=' \
               'g.page.m.rc._&laa=merchant-web-dashboard-card'

        d = {'Название': "📍 Mr.White 1 (Русанівка)",
             'Открывается': 10,
             'Закрывается': 22,
             'Берег Киева': 'Левый',
             'Приветствие': text,
             'Меню ссылка': url,
             'Маршрут ссылка': url1,
             'Отзыв ссылка': url2,
             'Телефон': '+380632345566'}
        net_list.append(d)

        text = 'Вітаю тебе в Вайт2 Лівобережна!' \
               'Це другий проект від нашої команди. Великий зал, окрема віпка з PS та затишна літня тераса.' \
               'Що саме тебе цікавить?'
        url = 'https://mrwhite2.orty.io/'
        url1 = 'https://www.google.com/maps/dir//%D0%9A%D0%B0%D0%BB%D1%8C%D1%8F%D0%BD-%D0%B1%D0%B0%D1%80+Mr.White/' \
               'data=!4m6!4m5!1m1!4e2!1m2!1m1!1s0x40d4cf8be4aa83af:0xac210e508ab17786?sa=X&ved=2ahUKEwihoKuyxar3AhVry' \
               'oUKHbSBCYMQ9Rd6BAhLEAQ'
        url2 = 'https://g.page/r/CafqlQy9kj80EBE/review'
        d = {'Название': "📍 Mr.White 2 (Лівобережна)",
             'Открывается': 10,
             'Закрывается': 22,
             'Берег Киева': 'Левый',
             'Приветствие': text,
             'Меню ссылка': url,
             'Маршрут ссылка': url1,
             'Отзыв ссылка': url2,
             'Телефон': '+380682345566'}
        net_list.append(d)

        text = "Вітаю тебе в Містер Уайт 3 Центр!\n" \
               "В центрі твого улюбленого міста 2 зали, 3 vip кімнати з PS4 та PS5, кальяни, коктейлі, " \
               "кухня та безмежна любов наших хлопців!\nЩо саме тебе цікавить?"
        url = 'https://mrwhite3.orty.io/'
        url1 = 'https://www.google.com/search?q=%D0%9A%D0%B0%D0%BB%D1%8C%D1%8F%D0%BD-%D0%B1%D0%B0%D1%80+Mr.White+3' \
               '&hl=ru&authuser=0&sxsrf=ALiCzsaPPNFbEwF2FnPnBf_i_Yjp4lhJMg%3A1655278977381' \
               '&ei=gY2pYuDdFv-J9u8Plvq4mAU&ved=0ahUKEwigos3b-q74AhX_hP0HHRY9DlMQ4dUDCA4&uact=5' \
               '&oq=%D0%9A%D0%B0%D0%BB%D1%8C%D1%8F%D0%BD-%D0%B1%D0%B0%D1%80+Mr.White+3' \
               '&gs_lcp=Cgdnd3Mtd2l6EAMyBAgjECcyBQgAEIAEMgYIABAeEBYyBggAEB4QFjoHCCMQsAMQJ' \
               'zoHCAAQRxCwA0oECEEYAEoECEYYAFC0AljjAmCYBGgBcAF4AIABwAGIAcABkgEDMC4xmAEAoAEByAEJwAEB&sclient=gws-wiz#'
        url2 = 'https://g.page/r/CXGroZh_woPzEBE/review'

        d = {'Название': "📍 Mr.White 3 (Центр)",
             'Открывается': 10,
             'Закрывается': 22,
             'Берег Киева': 'Правый',
             'Приветствие': text,
             'Меню ссылка': url,
             'Маршрут ссылка': url1,
             'Отзыв ссылка': url2,
             'Телефон': '+380682345566'}
        net_list.append(d)

        text = """Вітаю тебе в Містер Уайт 4 Лукьʼянівка, четвертий проект мережі.
                    Затишний та невеличкий Уайт з основним залом, двома VIPʼками та душевным персоналом.
                    Що саме тебе цікавить?"""
        url = 'https://mrwhite4.orty.io/'
        url1 = 'https://www.google.com/search?q=%D0%BA%D0%B0%D0%BB%D1%8C%D1%8F%D0%BD+%D0%B1%D0%B0%D1%80+' \
               'mr+white+4+gastro&hl=ru&authuser=0&sxsrf=ALiCzsbfR-2ewM3vlnIXBBAGEuS5ed7KaA%3A1655287796378' \
               '&ei=9K-pYtHQFqim9u8P_cWfuAg&oq=%D0%9A%D0%B0%D0%BB%D1%8C%D1%8F%D0%BD-%D0%B1%D0%B0%D1%80+Mr.White+3' \
               '&gs_lcp=Cgdnd3Mtd2l6EAEYATIHCCMQsAMQJzIHCAAQRxCwAzIHCAAQRxCwAzIHCAAQRxCwAzIHCAAQRxCwAzIHCAAQRxCwA' \
               'zIHCAAQRxCwAzIHCAAQRxCwAzIHCAAQRxCwA0oECEEYAEoECEYYAFAAWABgjQ5oAXABeACAAQCIAQCSAQCYAQDIAQnAAQE' \
               '&sclient' \
               '=gws-wiz#'
        url2 = 'https://g.page/r/CTXpcMpUfh-PEBE/review'

        d = {'Название': "📍 Mr.White 4 ( Лук‘янівська)",
             'Открывается': 10,
             'Закрывается': 22,
             'Берег Киева': 'Правый',
             'Приветствие': text,
             'Меню ссылка': url,
             'Маршрут ссылка': url1,
             'Отзыв ссылка': url2,
             'Телефон': '+380682345566'}
        net_list.append(d)

        text = """Вітаю тебе в Корнері aka Mr.White 5!
            Це перший заклад в Києві, де поєднані 2 різних формати:
            Спортивний Пив Бар на першому поверсі з великим асортиментом розливного і закусками
            Та затишний Лаунж Бар на мінус першому поверсі з коктельною картою, смачною кухнею і кальяном"""
        text += "\nМожеш не обирати спортивні трансляціі, чи якісний кальян - будь володарем свого життя" \
                " та отримуй все що хочеш ;)"
        url = 'https://corner12.orty.io/'
        url1 = 'https://www.google.com/maps/dir//%D0%9A%D0%B0%D0%BB%D1%8C%D1%8F%D0%BD-%D0%B1%D0%B0%D1%80+Mr.White/' \
               'data=!4m6!4m5!1m1!4e2!1m2!1m1!1s0x40d4cf8be4aa83af:0xac210e508ab17786?sa=X&ved=2ahUKEwihoKuyxar3AhVry' \
               'oUKHbSBCYMQ9Rd6BAhLEAQ'
        url2 = 'https://www.google.com/maps/place//data=!4m3!3m2!1s0x40d4cf8be4aa83af:0xac210e508ab17786!12e1?source=' \
               'g.page.m.rc._&laa=merchant-web-dashboard-card'

        d = {'Название': "📍 Corner 12 (Русанівка)",
             'Открывается': 10,
             'Закрывается': 22,
             'Берег Киева': 'Левый',
             'Приветствие': text,
             'Меню ссылка': url,
             'Маршрут ссылка': url1,
             'Отзыв ссылка': url2,
             'Телефон': '+380971161212'}
        net_list.append(d)

        d = {}
        for i in range(1, 6):
            d[i] = net_list[i - 1]
    return d


def create_json(file_name):
    with open(file_name + '.json', mode='wt', encoding='utf-8') as f:
        json.dump(fill_data(file_name), f, indent=2, ensure_ascii=False)


create_json('options')
create_json('заведения')
create_json('tokens')
