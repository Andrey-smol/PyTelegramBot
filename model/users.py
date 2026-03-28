import sqlalchemy as sq

from model.db_base import Base


class Users(Base):
    __tablename__ = "users"

    id = sq.Column(sq.Integer, primary_key=True, autoincrement=True)
    user_id_bot = sq.Column(sq.String, nullable=False, unique=True)
    date_registration = sq.Column(sq.String, nullable=False)
