from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField, BooleanField, IntegerField
from wtforms.validators import DataRequired


class AddEventForm(FlaskForm):
    event = StringField('Event Title', validators=[DataRequired()])
    description = StringField('Description', validators=[DataRequired()])
    date = StringField('Date', validators=[DataRequired()])
    address = StringField('Address', validators=[DataRequired()])
    is_moderated = BooleanField('Is_moderated', validators=[DataRequired()])
    picture = StringField('Picture', validators=[DataRequired()])


    submit = SubmitField('Submit')
