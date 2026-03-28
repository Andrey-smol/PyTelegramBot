import random

import requests
import telebot
from telebot import types, State, custom_filters

from config.config import Config_
from exception.exception import MyException
from log.logger import OperationLogger
from utils.enum_command import CommandsBot
from utils.enum_state import StateUser
from utils.user_bot import UserBot


class BotController:
    __TELEGRAM_API = Config_.telegram_api()
    __TOKEN = Config_.bot_token()
    __COMMANDS = {'NEXT': 'Дальше ⏭', 'DELETE_WORD': 'Удалить слово🔙', 'ADD_WORD': 'Добавить слово ➕'}
    __NEED_COMMAND_DICT_STR = "Надо сначала ввести команду: /start"

    def __init__(self, service):
        self.__service = service
        self.__bot = telebot.TeleBot(self.__TOKEN)
        self.__target_word = State()
        self.__translate_word = State()
        self.__another_words = State()
        self.__buttons = []
        self.__state = StateUser.start
        self.users = {}
        self.logger = OperationLogger()

        self.__bot.message_handler(commands=['start'])(self._start_dict)
        self.__bot.message_handler(commands=['help'])(self._send_help)
        self.__bot.message_handler(func=lambda m: m.text == self.__COMMANDS['NEXT'])(self._next_cards)
        self.__bot.message_handler(func=lambda m: m.text == self.__COMMANDS['DELETE_WORD'])(self._delete_word_menu)
        self.__bot.message_handler(func=lambda m: m.text == self.__COMMANDS['ADD_WORD'])(self._add_word_menu)
        self.__bot.message_handler(func=lambda m: True, content_types=['text'])(self._reply_message)

    @property
    def bot(self):
        return self.__bot

    @property
    def service(self):
        return self.__service

    @property
    def buttons(self):
        return self.__buttons

    @staticmethod
    def _check_telegram_token(timeout_: float = 5.0):
        if not BotController.__TOKEN:
            raise MyException("_check_telegram_token", "Error: Telegram token is empty")
        try:
            resp = requests.get(f"{BotController.__TELEGRAM_API}/bot{BotController.__TOKEN}/getMe", timeout=timeout_)
            if resp.status_code != 200:
                raise MyException("_check_telegram_token", f"Telegram API returned status {resp.status_code}")
            data = resp.json()
            if not data.get("ok"):
                raise MyException("_check_telegram_token", f"Telegram API response not ok: {data}")
        except requests.RequestException as e:
            raise MyException("_check_telegram_token", f"Error: Telegram token check failed: {e}")

    def start_bot(self):
        self.bot.add_custom_filter(custom_filters.StateFilter(self.bot))
        self.bot.infinity_polling(skip_pending=True, timeout=10, long_polling_timeout=5)

    def stop_bot_(self):
        if self.bot:
            print('stop_bot_')
            self.logger.log('Остановка бота')
            self.bot.stop_polling()

    def _send_help(self, message):
        """
        Handler of the /help command
        :param message:
        :return:
        """
        self.logger.log(f'user_id={message.from_user.id}, chat_id={message.chat.id} - команда /help')
        user_bot = self.users.setdefault(message.from_user.id, UserBot(message.from_user.id, message.chat.id))
        user_bot.state_bot = StateUser.start
        self.bot.reply_to(message, f'Я знаю команды: {[v.value for v in CommandsBot]}')
        mess = [
            "Команда /dict для входа в обучение английскому словарю.",
            "Вы можете:",
            "выбрать одно из предложенных четырёх английских слов,",
            f" добавить слово на русском языке ({self.__COMMANDS['ADD_WORD']}),",
            f"можете удалить слово на русском языке ({self.__COMMANDS['DELETE_WORD']}),",
            f"можете запросить следующее слово ({self.__COMMANDS['NEXT']})."
        ]
        self.bot.send_message(message.chat.id, self.show_hint(*mess))

    def _start_dict(self, message):
        """
        Handler of the /start command
        :param message:
        :return:
        """
        self.logger.log(f'user_id={message.from_user.id}, chat_id={message.chat.id} - команда /start')
        chat_id = message.chat.id
        user_id = message.from_user.id

        user_bot = self.users.setdefault(user_id, UserBot(user_id, chat_id))
        if user_bot.state_bot == StateUser.start:
            self.bot.send_message(chat_id, self.menu_greeting())
        user_bot.state_bot = StateUser.dict

        markup = types.ReplyKeyboardMarkup(row_width=2)
        word_dict = self.service.next_word(user_bot)
        if word_dict is None:
            self.bot.send_message(chat_id, user_bot.state_request.value)
            return
        self.bot.send_message(message.chat.id, f'У вас слов в словаре: {user_bot.count_words}')

        target_word = word_dict.dict_['word_rus']
        translate = word_dict.dict_['word_en']
        others = word_dict.dict_['others']
        self.__buttons = self._set_buttons(word_dict)
        markup.add(*self.buttons)

        greeting = f"Выбери перевод слова:\n🇷🇺 {target_word}"
        self.bot.send_message(chat_id, greeting, reply_markup=markup)
        self.bot.set_state(user_id, self.__target_word, chat_id)
        with self.bot.retrieve_data(user_id, chat_id) as data:
            data['target_word'] = target_word
            data['translate_word'] = translate
            data['other_words'] = others

    def _reply_message(self, message):
        """
        Text Message Handler - content_types=['text']
        :param message:
        :return:
        """
        text = message.text
        user_bot = self.users.setdefault(message.from_user.id, UserBot(message.from_user.id, message.chat.id))

        if user_bot.state_bot == StateUser.key_add:
            self._add_word(message)
            return
        if user_bot.state_bot == StateUser.key_del:
            self._delete_word(message)
            return
        if user_bot.state_bot != StateUser.dict:
            self.bot.send_message(message.chat.id, self.__NEED_COMMAND_DICT_STR)
            return

        markup = types.ReplyKeyboardMarkup(row_width=2)
        with self.bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            target_word = data['translate_word']
            if text == target_word:
                hint = self.show_target(data)
                hint_text = ["Отлично!❤", hint]
                hint = self.show_hint(*hint_text)
            else:
                for btn in self.buttons:
                    if btn.text == text:
                        btn.text = text + '❌'
                        break
                hint = self.show_hint("Допущена ошибка!",
                                      f"Попробуй ещё раз вспомнить слово 🇷🇺{data['target_word']}")
        markup.add(*self.buttons)
        self.bot.send_message(message.chat.id, hint, reply_markup=markup)

    def _next_cards(self, message):
        """
        handler for clicking on inline buttons - COMMANDS['NEXT']
        :param message:
        :return:
        """
        user_bot = self.users.setdefault(message.from_user.id, UserBot(message.from_user.id, message.chat.id))

        if user_bot.state_bot == StateUser.start:
            self.bot.send_message(message.chat.id, self.__NEED_COMMAND_DICT_STR)
            return
        user_bot.state_bot = StateUser.dict
        user_id = message.from_user.id
        chat_id = message.chat.id
        markup = types.ReplyKeyboardMarkup(row_width=2)
        word_dict = self.service.next_word(user_bot)
        if word_dict is None:
            self.bot.send_message(chat_id, user_bot.state_request.value)
            return

        target_word = word_dict.dict_['word_rus']
        translate = word_dict.dict_['word_en']
        others = word_dict.dict_['others']
        self.__buttons = self._set_buttons(word_dict)
        markup.add(*self.buttons)

        greeting = f"Выбери перевод слова:\n🇷🇺 {target_word}"
        self.bot.send_message(chat_id, greeting, reply_markup=markup)
        self.bot.set_state(user_id, self.__target_word, chat_id)
        with self.bot.retrieve_data(user_id, chat_id) as data:
            data['target_word'] = target_word
            data['translate_word'] = translate
            data['other_words'] = others

    def _delete_word_menu(self, message):
        """
        handler for clicking on inline buttons - COMMANDS['DELETE_WORD']
        :param message:
        :return:
        """
        user_bot = self.users.setdefault(message.from_user.id, UserBot(message.from_user.id, message.chat.id))
        if user_bot.state_bot != StateUser.dict:
            self.bot.send_message(message.chat.id, 'Надо ввести команду /start')
            return
        user_bot.state_bot = StateUser.key_del
        mess = "Напишите слово, которое вы хотите удалить"
        self.bot.send_message(message.chat.id, mess)

    def _delete_word(self, message):
        user_bot = self.users.setdefault(message.from_user.id, UserBot(message.from_user.id, message.chat.id))
        word = message.text
        result = self.service.delete_word(user_bot, word)
        if not result:
            mess = user_bot.state_request.value
        else:
            mess = f"Слово: {word}, было удалено"
        self.bot.send_message(message.chat.id, mess)
        self.logger.log(f'user_id={message.from_user.id}, chat_id={message.chat.id} - удаление слова {word}: {mess}')
        self._next_cards(message)

    def _add_word_menu(self, message):
        """
        handler for clicking on inline buttons - COMMANDS['ADD_WORD']
        :param message:
        :return:
        """
        user_bot = self.users.setdefault(message.from_user.id, UserBot(message.from_user.id, message.chat.id))
        if user_bot.state_bot != StateUser.dict:
            self.bot.send_message(message.chat.id, 'Надо ввести команду /start')
            return
        user_bot.state_bot = StateUser.key_add
        mess = "Напишите слово, которое вы хотите добавить"
        self.bot.send_message(message.chat.id, mess)

    def _add_word(self, message):
        user_bot = self.users.setdefault(message.from_user.id, UserBot(message.from_user.id, message.chat.id))
        result = self.service.add_word(user_bot, message.text)
        mess = f"Слово: {message.text} - {result}, было добавлено" if result else user_bot.state_request.value
        self.logger.log(
            f'user_id={message.from_user.id}, chat_id={message.chat.id} - добавление слова {message.text}: {mess}')
        self.bot.send_message(message.chat.id, mess)
        self.bot.send_message(message.chat.id, f'У вас слов в словаре: {user_bot.count_words}')
        self._next_cards(message)

    @staticmethod
    def show_target(data):
        return f"{data['target_word']} -> {data['translate_word']}"

    @staticmethod
    def show_hint(*lines):
        return '\n'.join(lines)

    @staticmethod
    def _set_buttons(word_dict) -> list:
        """
        Using the built-in keyboard (Telebot)
        :param word_dict:
        :return list buttons:
        """
        buttons = []
        target_word_btn = types.KeyboardButton(word_dict.dict_['word_en'])
        buttons.append(target_word_btn)
        others = word_dict.dict_['others']
        other_words_btns = [types.KeyboardButton(word) for word in others]
        buttons.extend(other_words_btns)
        random.shuffle(buttons)
        next_btn = types.KeyboardButton(BotController.__COMMANDS['NEXT'])
        add_word_btn = types.KeyboardButton(BotController.__COMMANDS['ADD_WORD'])
        delete_word_btn = types.KeyboardButton(BotController.__COMMANDS['DELETE_WORD'])
        buttons.extend([next_btn, add_word_btn, delete_word_btn])

        return buttons

    @staticmethod
    def menu_greeting() -> str:
        mess = ['Привет 👋', 'Давай попрактикуемся в английском языке.',
                'Тренировки можешь проходить в удобном для себя темпе.'
                'У тебя есть возможность использовать тренажёр, как конструктор,'
                'и собирать свою собственную базу для обучения.',
                'Для этого воспрользуйся инструментами:',
                f'{BotController.__COMMANDS['ADD_WORD']}',
                f'{BotController.__COMMANDS['DELETE_WORD']}.',
                'Ну что, начнём ⬇️'
        ]
        return BotController.show_hint(*mess)

