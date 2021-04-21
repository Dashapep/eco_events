import datetime
import sqlalchemy
from sqlalchemy import orm

from . import db_session
from .db_session import SqlAlchemyBase
from .willcome import Willcome


class Events(SqlAlchemyBase):
    __tablename__ = 'events'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    event = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True, default=0)
    address = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    date = sqlalchemy.Column(sqlalchemy.String)
    is_finished = sqlalchemy.Column(sqlalchemy.Boolean, default=True)
    is_moderated = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    author = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"), nullable=True)
    picture = sqlalchemy.Column(sqlalchemy.String, nullable=True, default='')
    user = orm.relation('User')

    def __repr__(self):
        return f'<Event> {self.event}'

    def get_willcome(self):
        db_sess = db_session.create_session()
        count = len(db_sess.query(Willcome).filter(Willcome.event_id == self.id).all())
        return count
