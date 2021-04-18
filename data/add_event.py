from flask_wtf import FlaskForm
from wtforms import FileField, TextAreaField
from wtforms import SubmitField, StringField, BooleanField
from wtforms.validators import DataRequired


class AddEventForm(FlaskForm):
    event = StringField('Название события', validators=[DataRequired()])
    description = TextAreaField('Описание')
    date = StringField('Дата проведения', validators=[DataRequired()])
    address = StringField('Адрес проведения')
    is_moderated = BooleanField('Проверено')
    is_finished = BooleanField('Завершено')

    picture = FileField()

    submit = SubmitField('Отправить')
