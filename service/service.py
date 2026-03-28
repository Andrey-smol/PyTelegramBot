import os
import random
import re
from typing import Optional

from dictionary.yandex_dict import YandexDictionary
from utils.enum_state_request import StateRequest
from utils.user_bot import UserBot
from service.next_dict import NextDict

import inspect

if not hasattr(inspect, 'getargspec'):
    def getargspec(func):
        spec = inspect.getfullargspec(func)
        from collections import namedtuple
        ArgsSpec = namedtuple('ArgsSpec', 'args varargs keywords defaults')
        return ArgsSpec(spec.args, spec.varargs, spec.varkw, spec.defaults)
    inspect.getargspec = getargspec

from pymorphy2 import MorphAnalyzer  # морфологический анализатор для русского языка


class Service:

    __INITIAL_WORDS_FOR_USER = 10
    morph_analyzer = MorphAnalyzer(
        path=os.path.join(os.getcwd(), '.venv', 'Lib', 'site-packages', 'pymorphy2_dicts_ru', 'data'))

    def __init__(self, repository):
        self.__repository = repository

    @property
    def repo(self):
        return self.__repository

    def delete_word(self, user_bot: UserBot, word) -> bool:
        if user_bot.count_words <= self.__INITIAL_WORDS_FOR_USER:
            user_bot.state_request = StateRequest.not_del_only_initial_words
            return False
        user_id = user_bot.user_id
        result = self.repo.del_word(user_id, word)
        if result:
            user_bot.count_words -= 1
            if user_bot.count_words < user_bot.count_request:
                user_bot.count_request = 0
                user_bot.next_request = 0
            return True
        user_bot.state_request = StateRequest.no_word_into_db
        return False

    def add_word(self, user_bot: UserBot, word) -> Optional[str]:
        if word and len(word.strip()) >= 1:
            word = word.strip()
            if self._is_russian_word(word):
                word_en = self._dictionary(word)
                if word_en is None:
                    user_bot.state_request = StateRequest.error_translation
                    return None
                user_id = user_bot.user_id
                result = self.repo.add_word((word, word_en), user_id)
                if result:
                    user_bot.count_words += 1
                    return word_en
                else:
                    user_bot.state_request = StateRequest.error_add_word
            else:
                user_bot.state_request = StateRequest.no_russian_word
        else:
            user_bot.state_request = StateRequest.error_input_word
        return None

    def next_word(self, user_bot: UserBot) -> Optional[NextDict]:
        user_id = user_bot.user_id
        if not user_id:
            user_bot.state_request = StateRequest.error_user_id
            return None
        next_request = user_bot.next_request
        count_words = user_bot.count_words
        count_request = user_bot.count_request

        if count_words == 0:
            count_words = self.repo.get_count_words_user(user_id)
            if count_words == 0:
                count_words = self.repo.init_start_words_for_user(user_id)
                if count_words == 0:
                    user_bot.state_request = StateRequest.no_words_for_user
                    return None
        word = self.repo.get_word_by_user_id(user_id, next_request)
        if word is None:
            user_bot.state_request = StateRequest.no_words_for_user
            return None
        next_request = word.id

        next_dict_ = NextDict()
        list_ = self.repo.get_words(user_id)
        if list_ and len(list_) > 4:
            next_dict_.dict_['others'] = random.sample([v[0] for v in list_ if v[0] != word.word_english], 3)
            next_dict_.dict_['word_rus'] = word.word_russian
            next_dict_.dict_['word_en'] = word.word_english

            count_request += 1
            if count_request >= count_words:
                next_request = 0
                count_request = 0
        else:
            user_bot.state_request = StateRequest.not_enough_words
        print(f'count_words={count_words}, next_request={next_request}, count_request={count_request}')
        user_bot.count_words = count_words
        user_bot.next_request = next_request
        user_bot.count_request = count_request
        return next_dict_

    @staticmethod
    def _is_russian_word(word) -> bool:
        russian = bool(re.fullmatch(r'[А-ЯЁа-яё\-]+', word))
        if not russian:
            return False
        if Service.morph_analyzer:
            parses = Service.morph_analyzer.parse(word)
            return bool(parses) and any('UNKN' not in p.tag for p in parses)
        return True

    @staticmethod
    def _dictionary(word_rus: str) -> Optional[str]:
        word_en = YandexDictionary.translate_word(word_rus)
        return None if word_en == '' else word_en
