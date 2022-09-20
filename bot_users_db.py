from sqlalchemy_utils import database_exists, create_database
from sqlalchemy import Boolean, Integer, BigInteger, String, DATETIME, Column, create_engine, select
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import datetime as dt
import json
import sqlalchemy.exc
import sys


# region utility
def my_create_engine():
    with open(r'Data\database_options.json', 'r') as file:
        db = json.load(file)
    conn_string = f"mariadb+mariadbconnector://{db['login']}:{db['password']}@{db['address']}/{db['name']}"
    try:
        return create_engine(conn_string,   pool_size=db['pool_size'], max_overflow=db['max_overflow'])
    except TypeError or sqlalchemy.exc.ArgumentError as error:
        print(f'Ошибка типа или аргумента при создании DB engine: {error}')

#  endregion


# region classes
class BotUser:
    engine = my_create_engine()
    base = None

    def __init__(self, chat_id: int):
        self.session, er = BotUser.create_session()
        if self.session is None:
            print(f'Работа программы завершена с ошибкой: {er.orig.msg}')
            sys.exit()
        self.user = self.session.query(User).get(chat_id)

    @classmethod
    def create_session(cls):
        try:
            cls.base.metadata.create_all(BotUser.engine)
        except sqlalchemy.exc.OperationalError as error:
            print(f'Ошибка коннектора при подключения к БД: {error}')
            return None, error
        except sqlalchemy.exc.ProgrammingError:
            my_create_engine()
            if not database_exists(cls.engine.url):
                create_database(cls.engine.url)
                if database_exists(cls.engine.url):

                    print(f"Database {d['name']} created succsessfull")
                cls.base.metadata.create_all(cls.engine)
        Session = sessionmaker()
        Session.configure(bind=cls.engine)
        return Session(), None


    def create(self, user_data, update_dates=True):
        now = dt.datetime.now()
        if update_dates:
            user_data.update({'created': now})
            user_data.update({'last': now})
        new_user = User(**user_data)
        self.session.add(new_user)
        self.session_commit()
        self.user = new_user

    def phone_number(self, num):
        self.user.phone_number = num
        self.session_commit()

    def last(self):
        self.user.last = dt.datetime.now()
        self.session_commit()

    def session_commit(self):
        try:
            self.session.commit()
        except sqlalchemy.exc.IntegrityError as error:
            print(f'Ошибка commit БД: {error}')

Base = declarative_base()
BotUser.base = Base
class User(Base):
    __tablename__ = 'users'
    id = Column(BigInteger, primary_key=True)
    full_name = Column(String(length=255))
    first_name = Column(String(length=255))
    last_name = Column(String(length=255))
    username = Column(String(length=50))
    is_premium = Column(Boolean)
    is_bot = Column(Boolean)
    phone_number = Column(String(length=20))
    language_code = Column(String(length=2))
    created = Column(DATETIME)
    last = Column(DATETIME)

    def __repr__(self):
        return f'{self.id}, {self.full_name}'

    @classmethod
    def get_users_list(cls, ses, filters: dict = None):
        if filters:
            return ses.query(User).filter_by(**filters).order_by(cls.created).all()
        return ses.execute(select(User).order_by(cls.created)).scalars().all()
#  endregion


if __name__ == '__main__':
    bot_user = BotUser(405329215)

    if bot_user.user is None:
        d = {"id": id, "full_name": 'Вася Пупкин', "phone": '0671234567'}
        bot_user.create(d)
        print(f'Запись добавлена: {bot_user.user}' if bot_user.user else 'ошибка добавления')
    else:
        print(f'Запись найдена: {bot_user.user}')
        bot_user.last_datetime_update()
        print('Дата и время обновлены')
    s, er = BotUser.create_session()
    users_list = User.get_users_list(s, filters={'full_name': 'Лиля Любая'})
    for u in users_list:
        print(u)
