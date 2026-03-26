
class NextDict:
    def __init__(self):
        self.dict_ = {'word_rus': ' ', 'word_en': ' ', 'others':[]}

    def __str__(self):
        return str({key:value for key, value in self.dict_.items()})
