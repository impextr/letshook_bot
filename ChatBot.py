import datetime as dt
import json
import csv
import locale as loc
import os
import platform
import bot_users_db as bu
import sqlalchemy as sql
import sqlalchemy.orm as sqlorm

import telegram
from telegram import *
from telegram.ext import *


# region Классы
class ChatBot:
    __doc__ = """1"""
    qnty_users = 0

    def __init__(self, update, context):
        ChatBot.qnty_users += 1
        self.chat_id = update.effective_chat.id
        self.update = update
        self.context = context
        # self.users = UsersList(update)
        self.remove_reply_keyboard = False

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

        self.spam = False
        self.spam_text = ''

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
        if not self.white:
            self.greating()
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
        self.send(photo=r'Data' '\\' + self.options['Имя файла общей заставки'])
        try:
            user_name = self.update.effective_user.full_name
        except ValueError or KeyError:
            user_name = ''
        if self.remove_reply_keyboard:
            markup = ReplyKeyboardRemove()
            message_id = self.context.bot.send_message(self.chat_id, text='', reply_markup=markup).message_id
            self.add_message(message_id)
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
        self.messages = []

    def add_message(self, message_id):
        self.messages.append(message_id)

    def create_menu_markup_buttons(self):
        if self.menu_level == 0:
            l1 = []
            button1 = InlineKeyboardButton(text='📍 Лівий берег', callback_data='Лівий берег')
            button2 = InlineKeyboardButton(text='📍 Правий берег', callback_data='Правий берег')
            l1.append([button1, button2])
            if self.chat_id in self.admins:
                button3 = InlineKeyboardButton(text='Получить файлы настроек', callback_data='Get file')
                button4 = InlineKeyboardButton(text='Подписчики', callback_data='Get followers')
                button5 = InlineKeyboardButton(text='Рассылка', callback_data='Spam')
                l1.append([button3])
                l1.append([button4])
                l1.append([button5])
            self.markup = InlineKeyboardMarkup(l1)
        elif self.menu_level == 1:
            d = self.hookahs
            hookah_list = []
            for i, v in d.items():
                if v['Берег Киева'] == self.side:
                    s = v['Название']
                    hookah_list.append([InlineKeyboardButton(text=s, callback_data='White ' + i)])
            b = InlineKeyboardButton(text='🔙Назад', callback_data='Всі заклади')
            hookah_list.append([b])
            self.markup = InlineKeyboardMarkup(hookah_list)
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
                                                  one_time_keyboard=True,
                                                  input_field_placeholder='')

            elif self.mode == 6:  # подтверждение брони
                button1 = InlineKeyboardButton(text="Так",
                                               callback_data='Подтверждение брони окончательное')
                button2 = InlineKeyboardButton(text="Відмова",
                                               callback_data='Всі заклади')
                self.markup = InlineKeyboardMarkup([[button1], [button2]])
            else:
                button1 = InlineKeyboardButton(text='🔙Назад', callback_data='White ' + self.white)
                self.markup = InlineKeyboardMarkup([[button1]])

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
            self.context.bot.send_message(i, text=text)
        log = Log(self)
        text = text.replace('\n', '')
        log.set(self.context, action_type=2, action=f'{event}: {text}')

        self.mode = 0
        self.booking = False
        self.complain = False
        self.greating()

    def booking_approval(self, finaly=False):
        if finaly:
            text = 'Дякую!\nНайближчим часом ми зателефонуємо щоб підтвердити твоє бронювання'
            self.menu_level = 0
            self.mode = 0
            self.send(text=text, markup=True)
            self.notify_about_event()
            return
        дата_и_время = dt.datetime.strftime(self.datetime, '%H:%M, %A %d %B')
        имя = self.user_name
        кво_гостей = self.qnty
        телефон = self.phone_number
        text = f"""Підтверждення замовлення:
White {self.white}
{дата_и_время},
ім'я: {имя}\nгостей: {кво_гостей}\nтелефон:{телефон}?"""
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

    def get_hookah_attr(self, attr_name):
        if self.white == '0':
            self.menu_level = 0
            self.greating()
            return
        return self.hookahs[self.white][attr_name]


class Log:
    """Фиксация ключевых событий в csv-файле"""

    def __init__(self, b):
        self.timestamp = str(dt.datetime.now())
        self.chat_id = b.update.effective_chat.id
        self.full_name = b.update.effective_chat.full_name
        self.white = b.white
        self.action_type = None
        self.action = None
        self.error = None

    def set(self, context, action_type, action, error=None):
        self.action_type = action_type
        self.action = action
        self.error = error
        filename = r'Data\log.csv'
        is_file = os.path.isfile(filename)
        with open(filename, 'a', encoding="utf-8", newline='') as __file:
            headers = ['timestamp', 'white', 'chat_id', 'full_name', 'action_type', 'action', 'error']
            __writer = csv.writer(__file, delimiter=';')
            parl = [self.timestamp, self.white, self.chat_id, self.full_name, self.action_type, self.action, self.error]
            if not is_file:
                __writer.writerow(headers)
            try:
                __writer.writerow(parl)
            except UnicodeEncodeError:
                context.bot.send_message(405329215, text=f'Ошибка записи csv: {parl}')
# endregion


# region initialization and others
def load_json(filename):
    full_path = fR"Data\{filename}"
    with open(full_path, 'rt', encoding='utf-8') as file:
        d = json.load(file)
    if 'Список администраторов' in d:
        d['Список администраторов'] = [int(i) for i in d['Список администраторов']]
    return d


def create_start():
    buttons = [KeyboardButton(text="/start")]
    return ReplyKeyboardMarkup(resize_keyboard=True, keyboard=[buttons])


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
    bot_user = context.user_data['bot_user']

    button_data = update.callback_query.data
    log = Log(b)
    log.set(context, action_type=1, action=button_data)
    if button_data == 'Всі заклади':
        b.delete_messages()
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
        b.send(text=None, photo=fr'Data\White{b.white}\mw1.jpg')
        b.send(text=d['Приветствие'] + f"\n\nЧас роботи: з {d['Открывается']} до {d['Закрывается']} \n\n")

        b.send(text='Що саме тебе цікавить?', markup=True)
    elif button_data[:13] == 'Фотки закладу':
        b.white = button_data[13:]
        b.show_photos()
    elif button_data == 'Зателефонувати':
        b.menu_level = 3
        b.send(text='Щоб зателефонувати, натисни на номер.')
        b.send(text=b.get_hookah_attr('Телефон'), markup=True)
    elif button_data == 'Get file':
        if os.path.isfile(r'Data\log.csv'):
            context.bot.send_document(b.chat_id, open(r'Data\log.csv', 'rb'), timeout=30, reply_markup=create_start())
        else:
            b.send(text='Не обнаружен файл настроек "options.json"', reply_markup=create_start())
        if os.path.isfile(r'Data\options.json'):
            context.bot.send_document(b.chat_id, open(r'Data\options.json', 'rb'), timeout=30, reply_markup=create_start())
        else:
            b.send(text='Не обнаружен файл настроек "options.json"', reply_markup=create_start())
        if os.path.isfile(r'Data\заведения.json'):
            context.bot.send_document(b.chat_id, open(r'Data\заведения.json', 'rb'), timeout=30, reply_markup=create_start())
        else:
            b.send(text='Не обнаружен файл с параметрами заведений "заведения.json"', reply_markup=create_start())
    elif button_data == 'Get followers':
        # try:
        #     users_list = b.users.users_list
        # except KeyError:
        #     users_list = UsersList(update).users_list
        s, er = bot_user.create_session()
        users_list = bu.User.get_users_list(s)

        s = ''
        for i, user in enumerate(users_list):
            phone = user.phone_number
            if phone:
                phone = f" {user.phone_number}, "
            if (i+1) % 50:
                s += f"{i+1}) {user.full_name}, {phone} язык: {user.language_code}\n"
            else:
                context.bot.send_message(b.chat_id, text=s, timeout=30)
                s = ''
        if s:
            context.bot.send_message(b.chat_id, text=s, timeout=20)
    elif button_data[:15] == 'Забукати столик':
        if len(button_data) > 15:
            b.white = button_data[15:]
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
        b.booking = False
        b.mode = 2
        b.menu_level = 3
        text = 'Коли ти в нас був?\nОбери найближчу дату, або напиши в форматі "21.08.2022"?'
        b.send(text=text, markup=True)
    elif button_data == 'Акції':
        b.menu_level = 3
        b.send(text=b.get_hookah_attr('Акции'), markup=True)
    elif button_data == 'wi-fi':
        b.menu_level = 3
        b.send(text=b.get_hookah_attr('Пароль'), markup=True)
    elif button_data == 'Подтверждение брони окончательное':
        b.booking_approval(finaly=True)
    elif button_data == 'Spam':
        b.send(text='Hello, admin!\nОтправь текст рассылки')
        b.spam = True
    elif button_data == 'Spam_yes':
        try:
            # users = b.context.user_data['users'].users_list
            s, er = bu.create_session()
            users_list = User.get_users_list(s)
        except KeyError or AttributeError:
            b.send("Ошибка получения списка рассылки")
            return
        b.menu_level = 3
        booking_hookah_number = '2'
        button1 = InlineKeyboardButton(text='⏰ Столик', callback_data='Забукати столик' + booking_hookah_number)
        button2 = InlineKeyboardButton(text='Головне меню', callback_data='Всі заклади')
        markup = InlineKeyboardMarkup([[button1, button2]])
        file_name = 'pict.jpg'
        photo = r'Data' '\\' + file_name
        if not os.path.isfile(photo):
            b.send(text=f'Файл фото не обнаружен: {photo}')
            return
        for u in users_list:
            if str(b.chat_id) != u['chat_id']:
                try:
                    message_id = context.bot.send_photo(u.id, photo=open(photo, 'rb'), timeout=30).message_id
                    b.add_message(message_id)
                    message_id = context.bot.send_message(u.id, text=b.spam_text, reply_markup=markup).\
                        message_id
                    b.add_message(message_id)
                    b.send(f"Отправка: {u.full_name}")
                except:
                    b.send(f"Ошибка отправки, пропущен: {u.full_name}")
        b.spam = False
        b.spam_text = ''
        b.menu_level = 0
        b.greating()
    if button_data == 'Spam_no':
        b.spam = False
        b.spam_text = ''
        b.menu_level = 0
        b.greating()


def get_answer_from_user(update, context):
    try:
        get_text = update.message.text
    except AttributeError:
        return
    try:
        b = context.user_data['bot']
    except KeyError:
        b = ChatBot(update, context)
        context.user_data['bot'] = b

    if b.spam:
        b.spam_text = get_text

        button1 = InlineKeyboardButton(text='Отправить', callback_data='Spam_yes')
        button2 = InlineKeyboardButton(text='Отмена', callback_data='Spam_no')
        markup = InlineKeyboardMarkup([[button1, button2]])
        text = 'Контроль текста рассылки:\n\n' + get_text
        b.add_message(context.bot.send_message(b.chat_id, text=text, reply_markup=markup).message_id)

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


def start(update, context):
    user = update.effective_user
    bot_user = bu.BotUser(user.id)
    if bot_user.user is None:
        d = {"id": user.id,
             "is_bot": user.is_bot,
             "language_code": user.language_code,
             "is_premium": user.is_premium,
             "first_name": user.first_name,
             "last_name": user.last_name,
             "full_name": user.full_name,
             "username": user.username}
        bot_user.create(d)
    else:
        bot_user.last()
    b = ChatBot(update, context)
    # b.users.write_file()
    context.user_data['bot'] = b
    context.user_data['bot_user'] = bot_user
    log = Log(b)
    log.set(context, action_type=0, action='start')
    b.greating()


def get_contact(update, context):
    try:
        b = context.user_data['bot']
    except KeyError:
        b = ChatBot(update, context)
        context.user_data['bot'] = b
    num = update.message.contact.phone_number
    bot_user = context.user_data['bot_user']
    bot_user.phone_number(num)
    if num[0] != '+':
        num = '+' + num
    b.phone_number = num
    # b.users.update_phone(b.phone_number)
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
        with open(r'Data' '\\' + file_name, 'wb') as f:
            context.bot.get_file(update.message.document).download(out=f)
    except Exception as excep:
        context.bot.reply_to(update.message, excep)
# endregion


# region Основная часть - запуск


updater = Updater(my_token)
dp = updater.dispatcher

dp.add_handler(CommandHandler("start", start))
dp.add_handler(MessageHandler(filters=Filters.text, callback=get_answer_from_user))
dp.add_handler(MessageHandler(filters=Filters.contact, callback=get_contact))
dp.add_handler(MessageHandler(filters=Filters.location, callback=get_location))
dp.add_handler(MessageHandler(filters=Filters.document, callback=get_file))
dp.add_handler(InlineQueryHandler(inlineKeyboard, pass_update_queue=True, pass_job_queue=True, pass_user_data=True))
dp.add_handler(CallbackQueryHandler(inlineKeyboard))

#  session, er = bu.create_session()

try:
    updater.start_polling()
except telegram.error.NetworkError as e:
    print(f'Ошибка запуска бота: {e}')
#  endregion
