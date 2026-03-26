import sqlalchemy as sq
from sqlalchemy.sql.schema import UniqueConstraint

from model.db_base import Base


class Words(Base):
    __tablename__ = "words"

    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    word_russian = sq.Column(sq.String(length=25), nullable=False)
    word_english = sq.Column(sq.String(length=25), nullable=False)

    __table_args__ = (UniqueConstraint("word_russian", "word_english", name="u_words_pair"),)

    def __str__(self):
        return f'id:{self.id}, word_russian:{self.word_russian}, word_english:{self.word_english}'
