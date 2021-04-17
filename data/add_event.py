from flask_wtf import FlaskForm
from wtforms import FileField
from wtforms import SubmitField, StringField, BooleanField, IntegerField
from wtforms.validators import DataRequired


class AddEventForm(FlaskForm):
    event = StringField('Название события', validators=[DataRequired()])
    description = StringField('Описание', validators=[DataRequired()])
    date = StringField('Дата проведения', validators=[DataRequired()])
    address = StringField('Адрес проведения', validators=[DataRequired()])
    is_moderated = BooleanField('Is_moderated', validators=[DataRequired()])
    # picture = FileField('Picture', validators=[DataRequired()])
    picture = FileField()



    submit = SubmitField('Отправить на модерацию')
