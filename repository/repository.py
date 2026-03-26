# pip install psycopg2
# pip install sqlalchemy
import json
from typing import Optional

import sqlalchemy
from sqlalchemy.orm import sessionmaker

from config.config import Config_
from exception.exception import MyException
from files.file_json import write_file_data
from model.db_base import Base
from model.user_word import UserWord
from model.users import Users
from model.words import Words


class Repository:
    def __init__(self):
        self.__driver = Config_.db_driver()
        self.__host = Config_.db_host()
        self.__user = Config_.db_user()
        self.__password = Config_.db_password()
        self.__db_name = Config_.db_name()
        self.__SessionFactory = self.__make_session()
        self.filling_table_from_file()

    @property
    def session(self):
        return None if self.__SessionFactory is None else self.__SessionFactory()

    def get_engine(self):
        dsn = self.__get_dsn()
        return sqlalchemy.create_engine(dsn)  # абстракция для подключения к базе данных

    def __get_dsn(self) -> str:
        dsn = f'{self.__driver}://{self.__user}:{self.__password}@{self.__host}/{self.__db_name}'
        print(dsn)
        return dsn

    def __make_session(self):
        engine = self.get_engine()
        if not engine:
            raise MyException('Repository', 'engine is none')
        self.create_tables(engine)
        return sessionmaker(bind=engine)

    def add_word(self, word_tuple, user_id) -> Optional[int]:
        if not word_tuple or not user_id:
            return None
        with self.session as s:
            try:
                id_ = self.__add_user(s, str(user_id))
                if id_:
                    rus, eng = word_tuple[0], word_tuple[1]
                    # Пытаемся найти существующее слово
                    id_word = (s.query(Words.id)
                               .filter(Words.word_russian == rus)
                               .one_or_none())
                    if id_word is None:
                        word_ = Words(word_russian=rus, word_english=eng)
                        s.add(word_)
                        s.flush()
                        word_id = word_.id
                    else:
                        word_id = id_word[0]
                        is_user_word = (s.query(UserWord.id)
                                        .filter(UserWord.id_word == word_id, UserWord.id_user == id_)
                                        .one_or_none())
                        if is_user_word:
                            return None

                    u_w = UserWord(id_user=id_, id_word=word_id)
                    s.add(u_w)
                    s.commit()
                return id_
            except Exception as e:
                raise MyException('Repository.add_word', f'error add word for {user_id=}')

    def get_word_by_user_id(self, user_id, word_id: int = 0) -> Optional[Words]:
        try:
            word = None
            with self.session as s:
                id_ = self.__add_user(s, user_id)
                if id_:
                    word = (s.query(Words)
                            .join(UserWord, Words.id == UserWord.id_word)
                            .filter(UserWord.id_user == id_, Words.id > word_id)
                            .order_by(Words.id.asc())
                            .limit(1).one_or_none()
                            # .first()
                            )
            return word
        except Exception as e:
            raise MyException('Repository.get_word_by_user_id', f'error get word for {user_id=}: {e}')

    def del_word(self, user_id, word) -> bool:
        try:
            with self.session as s:
                id_ = self.__get_user_id(s, user_id)
                if id_ is None:
                    return False
                id_word = self.__get_id_word_by_word(s, word)
                if id_word is None:
                    return False
                deleted = (s.query(UserWord)
                           .filter(UserWord.id_user == id_, UserWord.id_word == id_word)
                           .delete(synchronize_session=False))
                if deleted:
                    s.commit()
                    return True
                return False
        except Exception as e:
            raise MyException('Repository.del_word', f'error del {word=} for {user_id=}: {e}')

    def get_words(self, user_id) -> Optional[list]:
        with self.session as s:
            id_ = self.__get_user_id(s, user_id)
            if id_:
                return [v for v in (s.query(Words.word_english)
                                    .join(UserWord, UserWord.id_word == Words.id)
                                    .filter(UserWord.id_user == id_)
                                    .all())]
            return None

    @staticmethod
    def create_tables(engine):
        # Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    def filling_table_from_file(self):
        write_file_data()
        with self.session as s:
            query = s.query(Words.id).count()
            if query >= 10:
                return
            with open('files/data.json', encoding='utf-8') as fr:
                data = json.load(fr)
                for record in data:
                    model = {
                        'words': Words
                    }[record.get('model')]
                    s.add(model(**record.get('fields')))
            s.commit()

    def get_count_words_user(self, user_id) -> int:
        with self.session as s:
            return (s.query(Words.id)
                    .join(UserWord, Words.id == UserWord.id_word)
                    .join(Users, Users.id == UserWord.id_user)
                    .filter(Users.user_id == str(user_id))
                    .count())

    @staticmethod
    def __add_user(session_, user_id) -> Optional[int]:
        if user_id is None:
            raise MyException('Repository.add_user', f'error add {user_id=}')
        id_ = Repository.__get_user_id(session_, user_id)
        if not id_:
            user = Users(user_id=str(user_id))
            session_.add(user)
            session_.flush()
            id_ = user.id
            # query = session_.query(Words.id).filter(Words.id > 0, Words.id < 13).all()
            result = session_.query(Words.id).all()
            for v in result:
                session_.add(UserWord(id_user=id_, id_word=v[0]))
                session_.flush()
            session_.commit()
        return id_

    @staticmethod
    def __get_user_id(session_, user_id):
        q = session_.query(Users).filter(Users.user_id == str(user_id)).one_or_none()
        return None if q is None else q.id

    @staticmethod
    def __get_id_word_by_word(session_, word_rus) -> Optional[int]:
        id_ = session_.query(Words.id).filter(Words.word_russian == word_rus).one_or_none()
        return None if id_ is None else id_[0]
