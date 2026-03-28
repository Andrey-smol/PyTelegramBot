import json
from pathlib import Path

json_ =  [
    {
        'model': 'words',
        'fields': {
            'word_russian': 'шар',
            'word_english': 'ball'
        }
    },
    {
        'model': 'words',
        'fields': {
            'word_russian': 'стакан',
            'word_english': 'glass'
        }
    },
    {
        'model': 'words',
        'fields': {
            'word_russian': 'сегодня',
            'word_english': 'today'
        }
    },
    {
        'model': 'words',
        'fields': {
            'word_russian': 'он',
            'word_english': 'he'
        }
    },
    {
        'model': 'words',
        'fields': {
            'word_russian': 'наш',
            'word_english': 'our'
        }
    },
    {
        'model': 'words',
        'fields': {
            'word_russian': 'холод',
            'word_english': 'cold'
        }
    },
    {
        'model': 'words',
        'fields': {
            'word_russian': 'жираф',
            'word_english': 'giraffe'
        }
    },
    {
        'model': 'words',
        'fields': {
            'word_russian': 'нога',
            'word_english': 'leg'
        }
    },
    {
        'model': 'words',
        'fields': {
            'word_russian': 'голова',
            'word_english': 'head'
        }
    },
    {
        'model': 'words',
        'fields': {
            'word_russian': 'понедельник',
            'word_english': 'monday'
        }
    },
    {
        'model': 'words',
        'fields': {
            'word_russian': 'белый',
            'word_english': 'white'
        }
    },
    {
        'model': 'words',
        'fields': {
            'word_russian': 'зима',
            'word_english': 'winter'
        }
    }
]

def write_file_data():
    path_str = 'files/data.json'
    path_ = Path(path_str)
    if not path_.exists():
        with open(path_str, 'w', encoding='utf-8') as fw:
            json.dump(json_, fw, indent=4, ensure_ascii=False)


def get_tuple_start_words() -> tuple:
    return tuple(v['fields']['word_russian'] for v in json_)