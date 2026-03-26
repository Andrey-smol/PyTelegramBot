import requests

from config.config import Config_


class YandexDictionary:
    __URL = 'https://dictionary.yandex.net/api/v1/dicservice.json/lookup'
    __TOKEN = Config_.yandex_dict_token()

    @classmethod
    def translate_word(cls, word) -> str:
        # ваш код здесь
        trans_word = ''
        params = {
            'key': cls.__TOKEN,
            'lang': 'ru-en',
            'text': word
        }
        response = requests.get(cls.__URL, params=params)
        # Преобразуем JSON-ответ в Python-словарь
        data = response.json()
        # Проверяем, содержит ли ответ переводы
        if data.get('def'):
            trans_word = data['def'][0]['tr'][0]['text']
        return trans_word
