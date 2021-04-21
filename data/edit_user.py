from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Email


class EditUserForm(FlaskForm):
    surname = StringField('Фамилия')
    name = StringField('Имя', validators=[DataRequired()])
    age = IntegerField('Возраст')
    email = StringField('Адрес электронной почты', validators=[DataRequired()])
    moderator = BooleanField('Модератор')
    address = StringField('Адрес жительства')

    submit = SubmitField('Сохранить')
