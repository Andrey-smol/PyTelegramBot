import enum


class StateRequest(enum.Enum):
    ok = 'Нет ошибок'
    error_translation = 'Ошибка перевода слова'
    no_word_into_db = 'Нет слова в базе данных'
    not_del_only_initial_words = 'Слово не было удалено, в базе осталось только начальное количество слов'
    error_input_word = 'Ошибка при написании слова'
    no_russian_word = 'Слово не русского языка'
    error_add_word = 'Ошибка добавления слова'
    word_already_there = 'Слово уже есть в базе данных'
    error_user_id = 'Ошибка идентификатора пользователя'
    no_words_for_user = 'В базе не заданы слова для данного пользователя'
    not_enough_words = 'Не достаточно слов для данного пользователя'
