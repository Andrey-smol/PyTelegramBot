
# Telegram-бот для изучения английского языка
Курсовая работа по предмету "Базы данных" на тему "Telegram-бот для изучения английского языка".

## Возможности

- Подтверждение верного ответа и повтор при ошибке
- Пользователь может добавлять и удалять свои слова (они видны только ему)
  
## Требования
- Python 3.10+
- PostgreSQL 14+
- Telegram Bot Token

## Пошаговая настройка

### 1. Создание Telegram-бота и получение токена

#### Способ 1: Через @BotFather в Telegram
1. Откройте Telegram и найдите [@BotFather](https://t.me/botfather)
2. Отправьте команду `/newbot`
3. Укажите имя бота (например: "Netology_dict")
4. Укажите username (например: "netology_dict_bot") - должен заканчиваться на `_bot`
5. Скопируйте полученный токен (выглядит как `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

#### Способ 2: Через веб-интерфейс
1. Перейдите на [@BotFather](https://t.me/botfather) в браузере
2. Нажмите "Start" или отправьте `/start`
3. Выберите "Create a new bot" или отправьте `/newbot`
4. Следуйте инструкциям

#### Важно:
- **Сохраните токен** - он понадобится для настройки
- **Не делитесь токеном** - это ключ доступа к вашему боту
- **Токен можно пересоздать** командой `/revoke` у @BotFather

### 2. Установка зависимостей
```bash
# Создание виртуального окружения
python3 -m venv .venv

# Активация (macOS/Linux)
source .venv/bin/activate

# Установка пакетов
pip install -r requirements.txt
```

### 3. Настройка PostgreSQL

#### Установка PostgreSQL (macOS)
```bash
# Установка через Homebrew
brew install postgresql@14

# Запуск службы
brew services start postgresql@14

# Проверка статуса
brew services list | grep postgres
```

#### Установка PostgreSQL (Ubuntu/Debian)
```bash
# Обновление пакетов
sudo apt update

# Установка PostgreSQL
sudo apt install postgresql postgresql-contrib

# Запуск службы
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### Установка PostgreSQL (Windows)
1. Скачайте установщик с [официального сайта](https://www.postgresql.org/download/windows/)
2. Запустите установщик и следуйте инструкциям
3. Запомните пароль для пользователя postgres

### 4. Создание базы данных
```bash
# Подключение к PostgreSQL (macOS/Linux)
psql -U orionflash -d postgres

# Создание базы данных
CREATE DATABASE bot_dict;

# Создание пользователя (если нужно)
CREATE USER englishcard WITH PASSWORD 'postgres';

# Предоставление прав
GRANT ALL PRIVILEGES ON DATABASE englishcard TO englishcard;

# Выход
\q
```

### 5. Настройка конфигурации
```bash
# Копирование файла с примерами
cp config.sample.txt config.txt

# Редактирование config.txt
# Замените ВАШ_ТОКЕН_БОТА_ЗДЕСЬ на полученный токен
```

Содержимое файла `config.txt`:
```
# Конфигурация Telegram-бота NetologyDictBot
BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz

# Настройки базы данных
DB_HOST=localhost
DB_PORT=5432
DB_NAME=englishcard
DB_USER=orionflash
DB_PASSWORD=
```

### 6. Инициализация базы данных
```bash
# Применение схемы и заполнение начальными данными
python scripts/init_db.py
```

### 7. Иницализация  яндекс переводчика
Заходим на страницу [Dictionary API](https://yandex.com/dev/dictionary)
Для использования переводчика надо получить API key.
Полученный токен надо сохранить и использовать для **__YANDEX_DICT_TOKEN** в файле 
config.py



### 7. Запуск бота
```bash
# Запуск бота
python -m bot.main
```

## Структура базы данных

![](pictures/diagram_db.png)

### Таблицы:
1. **users** - пользователи бота
   - `id` (SERIAL PRIMARY KEY)
   - `used_id_bot` (TEXT)
   - `date_registration` (TEXT)

2. **words** - общий словарь для всех пользователей
   - `id` (SERIAL PRIMARY KEY)
   - `word_russian` (VARCHAR(25))
   - `word_english` (VARCHAR(25))

3. **user_word** - слова пользователей
   - `id` (SERIAL PRIMARY KEY)
   - `id_user` (INTEGER REFERENCES users.id)
   - `id_word` (INTEGER REFERENCES words.id)
   - CONSTRAINT u_words_pair UNIQUE("word_russian", "word_english")

## Структура проекта
```
PyTelegramBot/
├── controller/
│    └── bot_controller.py
├── service/
│    ├── service.py
│    └── next_dict.py
├── repository/
│    └── repository.py
├── model/
│    ├── db_base.py
│    ├── user_word.py
│    ├── users.py
│    └── words.py
├── config/
│    └── config.py
├── utils/
│    ├── enum_command.py
│    ├── enum_state.py 
│    ├── enum_state_request.py
│    └── user_bot.py
├── date_time/
│    └── date_time.py
├── dictionary/
│    └── yandex_dict.py 
├── exception/
│    └── exception.py
├── files/
│    └── file_json.py
├── log/
│    └── logger.py
├── pictures/
│    └── diagram_db.png
├── main.py
├── README.md
├── requirements.txt
└── .gitignore
```

## Использование бота

### Команды:
- `/start` - приветствие и главное меню

### Функции:
1. **Начать тренировку** - запуск тестирования с 4 вариантами ответа
2. **Добавить слово ➕** - добавление нового слова в формате "английское - русский"
3. **Удалить слово 🔙** - удаление слова из личной базы
4. **📊 Статистика** - просмотр статистики обучения
5. **⏹ Остановить игру** - остановка тренировки с результатами
6. **📊 Показать статистику** - статистика во время игры
7. **🔄 Сбросить статистику** - сброс всех данных статистики
8. **📈 Детальная статистика** - подробная статистика
9. **🏠 Главное меню** - возврат в главное меню

### Особенности:
- Минимум 4 слова для начала тренировки
- Пользовательские слова видны только их владельцу
- При добавлении слова показывается общее количество слов пользователя
- Неверные ответы позволяют попробовать снова
- **Отслеживание прогресса:**
  - Общее количество попыток
  - Процент успешных ответов
  - Текущая и лучшая серии правильных ответов
  - Время последней активности


## Морфологический анализ
Морфологический анализ - это определение характеристик слова на основе того, как это слово пишется. При морфологическом анализе не используется информация о соседних словах.

Для установки воспользуйтесь pip:

~~~
pip install pymorphy2
~~~

Словари распространяются отдельными пакетами:
~~~
pymorphy2-dicts-ru
~~~
Они обновляются время от времени; чтоб обновить словари, используйте
~~~
pip install -U pymorphy2-dicts-ru
~~~
Для установки требуются более-менее современные версии pip и setuptools.

В pymorphy2 для морфологического анализа слов есть класс MorphAnalyzer.

>>> import pymorphy2
>>> morph = pymorphy2.MorphAnalyzer()

https://pymorphy2.readthedocs.io/en/stable/user/guide.html





# Курсовая работа «Резервное копирование»

Возможна такая ситуация, что мы хотим показать друзьям фотографии из Интернета, но иногда сайты могут быть недоступны. Давайте защитимся от такого.  
Нужно написать программу для резервного копирования картинок с сайта про кошек в облачное хранилище Яндекс.Диск.  


## Задание:
1. Получить картинки кошек по API с сайта [cataas.com](https://cataas.com/) с текстом. Пример [api](https://cataas.com/cat/cute/says/hello) получения кошек с текстом на картинки 
2. Название папки должно совпадать с названием вашей группы в Нетологии
3. Текст картинки также должен являться названием файла на Яндекс.Диске
4. Сохранить json файл с информацией о размере файла картинки в json-файл
