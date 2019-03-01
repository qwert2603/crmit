from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import Length


class SendMessageForm(FlaskForm):
    body = TextAreaField('новое сообщение', validators=[Length(1, 1024)])
    submit = SubmitField('отправить')
