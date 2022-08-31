import datetime as dt
import json
import csv
import locale as loc
import os
import platform


from telegram import *
from telegram.ext import *


# region Классы
class ChatBot:
    qnty_users = 0

    def __init__(self, update, context):
        ChatBot.qnty_users += 1

        self.chat_id = update.effective_chat.id
        self.update = update
        self.context = context

        self.options = load_json('options.json')
        self.hookahs = load_json('заведения.json')

        self.side = ''
        self.white = '0'
        self.mode = 0
        self.when = ''
        self.datetime = dt.datetime.today()
        self.markup = ''
        self.qnty = 0

        self.booking = False
        self.user_name = ''
        self.phone_number = ''

        self.complain = False
        self.complain_text = ''
        self.menu_level = 0
        self.messages = []
        self.booking_receivers = self.options['Список получателей сообщения о резерве']
        self.complain_receivers = self.options['Список получателей сообщения о жалобе']
        self.admins = self.options['Список администраторов']
        self.admins = [int(i) for i in self.admins]

    def send(self, text=None, photo=None, markup=False):
        __doc__ = """
        Отправляет сообщение пользователю с фото и inline-кнопками
        параметры:
        photo: имя файла фотки в папке проекта
        markup: тэг с текстовой меткой варианта inline-кнопок (тэг распознаётся в процедуре create_inlinne_buttons)
        """
        context = self.context

        if photo is not None:
            if os.path.isfile(photo):
                message_id = context.bot.send_photo(self.chat_id, photo=open(photo, 'rb'), timeout=30).message_id
                self.add_message(message_id)
        if text is not None:
            if markup:
                self.create_menu_markup_buttons()
                message_id = context.bot.send_message(self.chat_id, text=text, reply_markup=self.markup).message_id
            else:
                message_id = context.bot.send_message(self.chat_id, text=text).message_id
            self.add_message(message_id)
            pass

    def create_time_buttons_markup(self):
        self.__doc__ = """Создаёт inline-кнопки на каждый час
        1) кнопки выводятся в несколько колонок, значение задается в переменной buttons_in_row
        2) начальное и конечное время определяются по времени начала и окончания работы заведения, берутся из настроек
        3) если дата = сегодня:
            а) для резерва начальное время = текущий час + 1, конечно - за час до окончания работы заведения
            б) для жалобы начальное время = время начала работы заведения, конечное - текущий час минус 1 
        """
        bottons_in_row = 3

        open_time = self.hookahs[self.white]['Открывается']
        close_time = self.hookahs[self.white]['Закрывается']

        start_time = 0
        stop_time = close_time

        if self.when == 'Today':
            if self.complain:
                start_time = open_time
                stop_time = dt.datetime.now().hour
            else:
                start_time = dt.datetime.now().hour
        else:
            stop_time = close_time

        if self.when == 'Yesterday':
            start_time = open_time
        if start_time < open_time:
            start_time = open_time
        else:
            if self.booking:
                start_time += 1
            else:
                if start_time == stop_time:
                    stop_time += 1

        buttons_text = []
        buttons = []
        buttons_row = []
        for i in range(start_time, stop_time, 1):
            buttons_text.append((i, f'{i}:00'))

        for i in range(len(buttons_text)):
            if i % bottons_in_row == 0 and i > 0:
                buttons.append(buttons_row)
                buttons_row = []
            время = buttons_text[i][0]
            buttons_row.append(InlineKeyboardButton(text=buttons_text[i][1], callback_data=f'Button_time{время}'))
        buttons.append(buttons_row)
        if start_time > stop_time:
            return False
        self.markup = InlineKeyboardMarkup(buttons).to_json()
        return True

    def greating(self):
        self.send(photo=self.options['Имя файла общей заставки'])
        try:
            user_name = self.update.effective_user.full_name
        except ValueError or KeyError:
            user_name = ''
        self.send(text=self.options['Общее приветствие 1'].format(user_name=user_name))
        self.send(text=self.options['Общее приветствие 2'], markup=True)

    def delete_messages(self):
        if not self.messages:  # нечего удалять
            return
        for i in self.messages:
            try:
                self.context.bot.delete_message(self.chat_id, message_id=i)
            except TelegramError:
                pass
                # if not self.context.bot.delete_message(self.chat_id, message_id=i):
            #     print(f'Сообщение не удалось удалить: {i}')
        self.messages = []

    def add_message(self, message_id):
        self.messages.append(message_id)

    def create_menu_markup_buttons(self):
        if self.menu_level == 1:
            d = self.hookahs
            hookah_list = []
            for i, v in d.items():
                if v['Берег Киева'] == self.side:
                    s = v['Название']
                    hookah_list.append([InlineKeyboardButton(text=s, callback_data='White ' + i)])
            b = InlineKeyboardButton(text='🔙Назад', callback_data='Всі заклади')
            hookah_list.append([b])
            self.markup = InlineKeyboardMarkup(hookah_list)
        elif self.menu_level == 0:
            l1 = []
            button1 = InlineKeyboardButton(text='📍 Лівий берег', callback_data='Лівий берег')
            button2 = InlineKeyboardButton(text='📍 Правий берег', callback_data='Правий берег')
            l1.append([button1, button2])
            if self.chat_id in self.admins:
                button3 = InlineKeyboardButton(text='Получить файлы настроек', callback_data='Get file')
                button4 = InlineKeyboardButton(text='Подписчики', callback_data='Get followers')
                l1.append([button3, button4])
            self.markup = InlineKeyboardMarkup(l1)
        elif self.menu_level == 2:
            d = self.hookahs[self.white]
            s = self.white

            button1 = InlineKeyboardButton(text='🍽️ Меню', url=d['Меню ссылка'])
            button2 = InlineKeyboardButton(text='⏰ Столик', callback_data='Забукати столик')
            button3 = InlineKeyboardButton(text='📷 Фотки закладу', callback_data='Фотки закладу' + s)
            button4 = InlineKeyboardButton(text='📍 Маршрут', url=d['Маршрут ссылка'])
            button5 = InlineKeyboardButton(text='🎁 Акції', callback_data='Акції')
            button6 = InlineKeyboardButton(text='📞 Зателефонувати', callback_data='Зателефонувати')
            button7 = InlineKeyboardButton(text='🎰 👕 Мерч', url='https://letshook.com.ua/merch')
            button8 = InlineKeyboardButton(text='🌐 Пароль від wi-fi', callback_data='wi-fi')
            button9 = InlineKeyboardButton(text='✏️Похвалити', url=d['Отзыв ссылка'])
            button10 = InlineKeyboardButton(text='🤬 Поскаржитись', callback_data='Поскаржитись')
            if self.side == "Правый":
                button11 = InlineKeyboardButton(text='🔙Назад', callback_data='Правий берег')
            else:
                button11 = InlineKeyboardButton(text='🔙Назад', callback_data='Лівий берег')

            self.markup = InlineKeyboardMarkup([[button1, button2],
                                                [button3, button4],
                                                [button5, button6],
                                                [button7, button8],
                                                [button9, button10],
                                                [button11]])
        elif self.menu_level == 3:
            if self.mode == 1:  # имя пользователя
                button1 = InlineKeyboardButton(text="Так, це я",
                                               callback_data='Так, це я')
                button2 = InlineKeyboardButton(text='Ні, зараз напишу',
                                               callback_data='Ні, зараз напишу')
                self.markup = InlineKeyboardMarkup([[button1, button2]])
            elif self.mode == 2:  # дата
                self.create_dates_buttons()
            elif self.mode == 3:  # время
                self.create_time_buttons_markup()
            elif self.mode == 4:
                pass
            elif self.mode == 5:  # запрос поделиться телефоном
                button1 = KeyboardButton(text="Поділитись телефоном", request_contact=True)
                buttons = [button1]
                if self.complain:
                    button2 = KeyboardButton(text="Залишитись анонімом")
                    buttons.append(button2)
                self.markup = ReplyKeyboardMarkup(resize_keyboard=True,
                                                  keyboard=[buttons],
                                                  selective=False,
                                                  one_time_keyboard=True,
                                                  input_field_placeholder='')

            elif self.mode == 6:  # подтверждение брони
                button1 = InlineKeyboardButton(text="Так",
                                               callback_data='Подтверждение брони окончательное')
                button2 = InlineKeyboardButton(text="Відмова",
                                               callback_data='Отказ от брони')
                self.markup = InlineKeyboardMarkup([[button1], [button2]])
            else:
                button1 = InlineKeyboardButton(text='🔙Назад', callback_data='White ' + self.white)
                self.markup = InlineKeyboardMarkup([[button1]])

        if not isinstance(self.markup, str):
            self.markup = self.markup.to_json()
        return

    def show_photos(self):
        self.menu_level = 3
        for i in range(1, 7):
            catalog = r'Data\White' + self.white
            file_name = catalog + fr'\White{i}.jpeg'
            if os.path.isfile(file_name):
                self.send(photo=file_name)
        text = 'Ось декілька фоток, більше можеш знайти на сайті www.letshook.com.ua'
        self.send(text=text, markup=True)

    def notify_about_event(self):
        white = self.white
        дата_и_время = dt.datetime.strftime(self.datetime, '%H:%M, %A %d %B')
        if self.booking:
            event = 'Резерв'
        else:
            event = 'Жалоба'
        if event == "Жалоба":
            event += ':\n' + self.complain_text

        text = ''
        if test_mode:
            text += '===Это тестирование===\n'
        text += f'Событие: {event}.\n' \
                f'White № {white}\n\n' \
                f"Телефон: {self.phone_number if self.phone_number else 'Анонім'}\n\n" \
                f'Дата и время события: {дата_и_время}\n'
        if self.user_name:
            text += f'Имя: {self.user_name}\n'
        if self.user_name:
            text += f'К-во гостей: {self.qnty}\n'
        for i in self.booking_receivers if self.booking else self.complain_receivers:
            self.chat_id = i
            self.send(text=text)
        self.mode = 0
        self.booking = False
        self.complain = False

    def booking_approval(self, finaly=False):
        if finaly:
            text = 'Дякую!\nНайближчим часом ми зателефонуємо щоб підтвердити твоє бронювання'
            self.menu_level = 2
            self.mode = 0
            self.send(text=text, markup=True)
            self.notify_about_event()
            return
        дата_и_время = dt.datetime.strftime(self.datetime, '%H:%M, %A %d %B')
        имя = self.user_name
        кво_гостей = self.qnty
        телефон = self.phone_number
        text = f"Підтверждення замовлення:\n{дата_и_время},\nім'я: {имя}\nгостей: {кво_гостей}\nтелефон:{телефон}?"
        self.mode = 6
        self.send(text=text, markup=True)

    def create_dates_buttons(self):
        loc.setlocale(loc.LC_ALL, "ukr_UKR")
        f_str = '%A %d %B %Y'

        today = dt.datetime.today()
        event = 'Booking' if self.booking else 'Сomplaint'
        d = [(today + dt.timedelta(days=i)).strftime(f_str) for i in range(-1, 2)]

        days = [('Today', 'Сьгодні:', d[1]),
                ('Yesterday', 'Вчора:', d[0]) if event == 'Сomplaint' else ('Tomorrow', 'Завтра', d[2]),
                ('OtherDate', 'Інша дата', '')]

        buttons_list = []
        for when in days:
            button = InlineKeyboardButton(text=f"{when[1]} {when[2]}", callback_data=event + when[0])
            buttons_list.append([button])
        self.markup = InlineKeyboardMarkup(buttons_list)

    def set_date(self, get_text):
        format_strings = ['%d.%m.%y', '%d.%m.%Y', '%d/%m/%y', '%d/%m/%Y', '%d-%m-%y', '%d-%m-%Y']
        for f in format_strings:
            try:
                self.datetime = dt.datetime.strptime(get_text, f)
                break
            except ValueError:
                continue
        else:
            self.datetime = dt.datetime.today()

    def get_time(self):
        self.mode = 3

        if self.complain:
            text = 'В який приблизно час?'
        else:
            if not self.create_time_buttons_markup():
                text = 'На жаль на сьогодні часу для резерву вже немає'
            else:
                text = 'На який час'

        self.send(text=text, markup=True)


class UsersList:
    """
        1. Читает данные из файла <file_name> формата <fily_type>
        2. Если файл не найден, то создаёт его и записывает
        3. Возвращает список пользователей из файла в виде словаря: <Key>=chat_id:<Prop> = список свойств в виде словаря
    """

    def __init__(self, file_type, message):
        self.file_type = file_type
        self.file_name = r'Data\Users.' + self.file_type
        self.message = message
        self.phone = ''
        self.language_code = message.from_user.language_code
        self.users_list = []
        self.get_users_list()
        self.user = self.get_current__user()

    def get_users_list(self):
        __file_exit = os.path.isfile(self.file_name)
        if not __file_exit:
            self.create_file()  # 02. создаёт пустой файл заданного типа
        self.read_users_list()  # 03. Прочитать список пользователей из файла
        if not self.current_user_in_list():  # # 04. Пользователь есть в списке?
            self.add_user()                 # 05. Добавить пользователя в список
            self.write_file(mode='a')     # 06. Записать список пользователей в файл

    def write_file(self, mode='w'):
        if self.file_type == 'json':
            with open(self.file_name, 'wt', encoding='utf-8') as __file:
                json.dump(self.users_list, __file, indent=2, ensure_ascii=False)
        elif self.file_type == 'csv':
            with open(r'Data\users.csv', mode, encoding="utf-8") as __file:
                __writer = csv.writer(__file, delimiter=';')
                for i in self.users_list:
                    __writer.writerow([i['chat_id'],
                                       i['full_name'],
                                       i['created'],
                                       i['last'],
                                       i['language_code']])

    def get_current_user(self):
        datetime_now_str = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return {'chat_id': str(self.message.chat.id),
                'full_name': self.message.from_user.full_name,
                'phone': self.phone,
                'created': datetime_now_str,
                'last': datetime_now_str,
                'language_code': self.language_code}

    def create_file(self):
        self.__doc__ = 'Создаёт и записывает пустой файл'
        if self.file_type == 'json':
            __users_list = []
            with open(self.file_name, 'w') as __file:
                json.dump(__users_list, __file, indent=2)
        elif self.file_type == 'csv':
            with open(r'Data\users.csv', 'a', encoding="utf-8") as __file:
                __file.close()

    def read_users_list(self):
        # 02. Прочитать список пользователей из файла
        if self.file_type == 'json':
            with open(self.file_name, 'r', encoding="utf-8") as file:
                self.users_list = json.load(file)
                if self.users_list[0].get('phone') is None:
                    for i in self.users_list:
                        i['phone'] = ''
        elif self.file_type == 'csv':
            self.read_userslist_from_csv()

    def current_user_in_list(self):  # 04. Пользователь есть в списке?
        for i in self.users_list:
            if i['chat_id'] == str(self.message.chat.id):
                return True
        return False

    def add_user(self):
        self.users_list.append(self.get_current_user())

    def read_userslist_from_csv(self):
        with open(self.file_name, 'r', encoding="utf-8") as file:
            __reader = csv.reader(file, delimiter=';')
            for row in __reader:
                if len(row) > 0:
                    self.users_list.append({'chat_id': row[0],
                                            'full_name': row[1],
                                            'created': row[2],
                                            'last': row[3],
                                            'language_code': row[4]})

    def get_current__user(self):
        for i in self.users_list:
            if i['chat_id'] == str(self.message.chat.id):
                return i
        return None

    def get_timedelta(self):
        if self.user is None:
            return 0
        delta = dt.datetime.now() - dt.datetime.strptime(self.user['last'], "%Y-%m-%d %H:%M:%S")
        self.user['last'] = dt.datetime.strftime(dt.datetime.now(), "%Y-%m-%d %H:%M:%S")
        return delta

    def update_phone(self, phone):
        self.user['phone'] = phone
        self.write_file()


# endregion


# region initialization
def load_json(filename):
    full_path = fR"Data\{filename}"
    with open(full_path, 'rt', encoding='utf-8') as file:
        d = json.load(file)
    if 'Список администраторов' in d:
        d['Список администраторов'] = [int(i) for i in d['Список администраторов']]
    return d


options = load_json('options.json')
tokens = load_json('tokens.json')

test_mode = platform.node() == 'Acer'
my_token = tokens['test'] if test_mode else tokens['main']
#  endregion


# region Handlers
def inlineKeyboard(update, context):
    try:
        b = context.user_data['bot']
    except KeyError:
        b = ChatBot(update, context)
        context.user_data['bot'] = b
    b.delete_messages()

    button_data = update.callback_query.data
    if button_data == 'Всі заклади':
        b.menu_level = 0
        b.greating()
    elif button_data == 'Лівий берег':
        b.menu_level = 1
        b.side = 'Левый'
        b.send(text='Лівий берег', markup=True)
    elif button_data == 'Правий берег':
        b.menu_level = 1
        b.side = 'Правый'
        b.send(text='Правий берег', markup=True)
    elif button_data[:5] == 'White':
        b.menu_level = 2
        b.white = button_data[6:]
        d = b.hookahs[b.white]
        text = d['Приветствие'] + f"\n\nЧас роботи: з {d['Открывается']} до {d['Закрывается']} \n\n"
        b.send(text=text)
        text = 'Що саме тебе цікавить?'
        b.send(text=text, photo=fr'White{b.white}\mw1.jpg', markup=True)
    elif button_data[:13] == 'Фотки закладу':
        b.white = button_data[13:]
        b.show_photos()
    elif button_data == 'Зателефонувати':
        b.menu_level = 3
        b.send(text='Щоб зателефонувати, натисни на номер.')
        b.send(text=b.hookahs[b.white]['Телефон'], markup=True)
    elif button_data == 'Get file':
        if os.path.isfile(r'Data\options.json'):
            context.bot.send_document(b.chat_id, open(r'Data\options.json', 'rb'), timeout=30)
        else:
            b.send(text='Не обнаружен файл настроек "options.json"')
        if os.path.isfile(r'Data\заведения.json'):
            context.bot.send_document(b.chat_id, open(r'Data\заведения.json', 'rb'), timeout=30)
        else:
            b.send(text='Не обнаружен файл с параметрами заведений "заведения.json"')
    elif button_data == 'Get followers':
        users_list = context.user_data['users'].users_list
        s = ''
        for i, user in enumerate(users_list):
            phone = user['phone']
            if phone:
                phone = f" {user['phone']}, "
            s += f"{i+1}) {user['full_name']}, {phone} язык: {user['language_code']}\n"
        b.send(text=s)
    elif button_data == 'Забукати столик':
        b.menu_level = 3
        b.booking = True
        b.mode = 1
        photo = 'White' + b.white + r'\mw1.jpg'
        text = f'Столик на твоє імʼя {update.effective_chat.full_name}, або ввести інше?'
        b.send(text=text, photo=photo, markup=True)
    elif button_data == 'Так, це я' or button_data == 'Ні, зараз напишу':
        if button_data == 'Ні, зараз напишу':
            return
        b.user_name = update.effective_chat.full_name
        b.menu_level = 3
        b.mode = 2
        text = 'На яку дату потрібен столик?'
        b.send(text=text, markup=True)
    elif button_data == 'Предложение выбрать дату резерва столика':
        b.menu_level = 3
        b.mode = 3
    elif button_data[:7] == 'Booking' or button_data[:9] == 'Сomplaint':
        if b.booking:
            b.when = button_data[7:]
        elif b.complain:
            b.when = button_data[9:]
        else:
            b.when = 'Today'

        if b.when == 'OtherDate':
            if b.booking:
                text = 'На яку дату потрібен столик? Напиши в форматі "21.08.22"'
            else:
                text = 'Коли ти в нас був?\nОбери найближчу дату, або напиши в форматі "21.08.22"?'
            b.send(text=text)
            return

        days = 0
        if b.when == 'Tomorrow':
            days = 1
        elif b.when == 'Yesterday':
            days = -1
        b.datetime = dt.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0) + dt.timedelta(days=days)
        b.get_time()
    elif button_data[:11] == 'Button_time':
        t = int(button_data[11:])
        b.datetime += dt.timedelta(hours=t)
        b.mode = 4
        if b.booking:
            text = 'На яку кількість осіб? Напиши числом'
        else:
            text = 'Що саме сталось?'
        b.send(text=text)
    elif button_data == 'Поскаржитись':
        text = 'Нам дуже прикро що ми залишили про себе погані згадки, ' \
               'розкажи будь ласка що сталось і ми спробуємо виправитись та реабілітуватись перед тобою'
        b.send(text=text)

        b.complain = True
        b.mode = 2
        b.menu_level = 3
        text = 'Коли ти в нас був?\nОбери найближчу дату, або напиши в форматі "21.08.2022"?'
        b.send(text=text, markup=True)
    elif button_data == 'Акції':
        b.menu_level = 3
        b.send(text=b.hookahs[b.white]['Акции'], markup=True)
    elif button_data == 'wi-fi':
        b.menu_level = 3
        b.send(text=b.hookahs[b.white]['Пароль'], markup=True)
    elif button_data == 'Подтверждение брони окончательное':
        b.booking_approval(finaly=True)


def get_answer_from_user(update, context):
    get_text = update.message.text
    try:
        b = context.user_data['bot']
    except KeyError:
        b = ChatBot(update, context)
        context.user_data['bot'] = b

    if b.mode == 1:
        b.user_name = get_text
        b.menu_level = 3
        b.mode = 2
        text = 'На яку дату потрібен столик?'
        b.send(text=text, markup=True)
    elif b.mode == 2:
        b.set_date(get_text)
        b.get_time()
    elif b.mode == 4 and b.booking:  # кол-во гостей
        n = 0
        if get_text.isdecimal():
            try:
                n = int(get_text)
            except ValueError or TypeError:
                b.send(text='Невірне значення. Введіте число.')
        b.qnty = n

        b.mode = 5
        b.send(text='Залиш свій мобільний, щоб ми могли підтвердити бронювання', markup=True)
    elif b.mode == 4 and b.complain:
        b.complain_text = get_text
        b.mode = 5
        b.send(text='Залиш свій мобільний, щоб ми могли звʼязатись з тобою в разі необхідності', markup=True)
    elif b.mode == 5:
        if get_text == "Залишитись анонімом":
            text = 'Дякую що не мовчиш, завдяки тобі ми спробуємо стати сильніше 💪'
            b.menu_level = 2
            b.mode = 0
            b.send(text=text, markup=True)
            b.notify_about_event()


def start_callback(update, context):
    users = UsersList(file_type='json', message=update.message)
    users.write_file()

    context.user_data.update({'users': users})

    b = ChatBot(update, context)
    context.user_data['bot'] = b
    b.greating()


def get_contact(update, context):
    try:
        b = context.user_data['bot']
    except KeyError:
        b = ChatBot(update, context)
        context.user_data['bot'] = b
    num = update.message.contact.phone_number
    if num[0] != '+':
        num = '+' + num
    b.phone_number = num
    users = context.user_data['users']
    users.update_phone(b.phone_number)
    b.delete_messages()

    if b.booking:
        b.booking_approval()
    elif b.complain:
        text = 'Дякую що не мовчиш, завдяки тобі ми спробуємо стати сильніше 💪'
        b.send(text=text)
        b.notify_about_event()


def get_location(update, context):
    b = context.user_data['bot']
    context.user_data['Location'] = update.message.location
    b.send(text=f'Дякуємо, локація зафіксована як: {str(update.message.location)}')


def get_file(update, context):
    b = context.user_data['bot']
    if b.chat_id not in b.options['Список администраторов']:
        b.send(text='У вас нет прав для отправки файлов.')
        return
    file_name = update.message.document.file_name
    if file_name != 'options.json' and file_name != 'заведения.json':
        b.send(text='Не верное имя файла.')
        return
    try:
        # file = context.bot.get_file(update.message.document.file_id)

        with open(r'Data' '\\' + file_name, 'wb') as f:
            context.bot.get_file(update.message.document).download(out=f)

    except Exception as e:
        context.bot.reply_to(update.message, e)
# endregion


# region Основная часть - запуск


updater = Updater(my_token)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start_callback))
dp.add_handler(MessageHandler(filters=Filters.text, callback=get_answer_from_user))
dp.add_handler(MessageHandler(filters=Filters.contact, callback=get_contact))
dp.add_handler(MessageHandler(filters=Filters.location, callback=get_location))
dp.add_handler(MessageHandler(filters=Filters.document, callback=get_file))
dp.add_handler(InlineQueryHandler(inlineKeyboard, pass_update_queue=True, pass_job_queue=True, pass_user_data=True))
dp.add_handler(CallbackQueryHandler(inlineKeyboard))

updater.start_polling()
#  endregion
