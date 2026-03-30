import os


class Config_:
    __BOT_TOKEN = os.getenv('BOT_TOKEN', '')
    __YANDEX_DICT_TOKEN = os.getenv('YANDEX_DICT_TOKEN', '')
    __URL_YANDEX_DICTIONARY = 'https://dictionary.yandex.net/api/v1/dicservice.json/lookup'
    __TELEGRAM_API = "https://api.telegram.org"

    __DB_DRIVER = os.getenv('DB_DRIVER', 'postgresql')
    __DB_HOST = os.getenv('DB_HOST', 'localhost:5432')  # localhost будет использоваться по умолчанию
    __DB_USER = os.getenv('DB_USER', 'postgres')  # postgres будет использоваться по умолчанию
    __DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')  # postgres по умолчанию
    __DB_NAME = os.getenv('DB_NAME', 'bot_dict')  # client_db будет использоваться по умолчанию

    @classmethod
    def bot_token(cls):
        return cls.__BOT_TOKEN

    @classmethod
    def yandex_dict_token(cls):
        return cls.__YANDEX_DICT_TOKEN

    @classmethod
    def db_driver(cls):
        return cls.__DB_DRIVER

    @classmethod
    def db_host(cls):
        return cls.__DB_HOST

    @classmethod
    def db_user(cls):
        return cls.__DB_USER

    @classmethod
    def db_password(cls):
        return cls.__DB_PASSWORD

    @classmethod
    def db_name(cls):
        return cls.__DB_NAME

    @classmethod
    def telegram_api(cls):
        return cls.__TELEGRAM_API

    @classmethod
    def url_yandex_dictionary(cls):
        return cls.__URL_YANDEX_DICTIONARY

