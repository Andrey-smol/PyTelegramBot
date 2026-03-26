import sqlalchemy as sq
from sqlalchemy.orm import relationship

from model.db_base import Base
from model.users import Users
from model.words import Words


class UserWord(Base):
    __tablename__ = "user_word"

    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    id_user = sq.Column(sq.Integer, sq.ForeignKey("users.id"), nullable=False)
    id_word = sq.Column(sq.Integer, sq.ForeignKey("words.id"), nullable=False)

    user = relationship(Users, backref="user_word")
    word = relationship(Words, backref="user_word")
