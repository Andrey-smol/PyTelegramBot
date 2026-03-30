import requests

from config.config import Config_
from exception.exception import MyException


class YandexDictionary:
    __URL = Config_.url_yandex_dictionary()
    __TOKEN = Config_.yandex_dict_token()

    @classmethod
    def translate_word(cls, word) -> str:
        if not word:
            return ''
        params = {
            'key': cls.__TOKEN,
            'lang': 'ru-en',
            'text': word
        }
        try:
            trans_word = ''
            response = requests.get(cls.__URL, params=params, timeout=5)
            response.raise_for_status()
            # Преобразуем JSON-ответ в Python-словарь
            data = response.json()
            # Проверяем, содержит ли ответ переводы
            if data.get('def'):
                trans_word = data['def'][0]['tr'][0]['text']
            return trans_word
        except Exception as e:
            return ''
