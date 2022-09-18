import json
import sqlalchemy
import bot_users_db as bu
import datetime as dt



with open(r'Data\users.json', 'r', encoding="utf-8") as file:
    l = json.load(file)
for i, user in enumerate(l):
    bot_user = bu.BotUser(user['chat_id'])
    if bot_user.user is None:
        d = {"id": int(user['chat_id']),
             "language_code": user['language_code'],
             "phone_number": user['phone'],
             "created": dt.datetime.strptime(user['created'], '%Y-%m-%d %H:%M:%S'),
             "last": dt.datetime.strptime(user['last'], '%Y-%m-%d %H:%M:%S'),
             "full_name": user['full_name']}
        bot_user.create(d, update_dates=False)
        print(f'{i}: запись добавлена: {bot_user.user}' if bot_user.user else 'ошибка добавления')
    else:
        print(f'Запись найдена: {bot_user.user}')
        bot_user.last()
        print('Дата и время обновлены')
