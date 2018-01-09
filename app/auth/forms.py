from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError
from wtforms.validators import Email, Length, DataRequired, EqualTo, Regexp
from app.models import SystemUser


class LoginForm(FlaskForm):
    login = StringField('логин или email', validators=[DataRequired(), Length(1, 64)])
    password = PasswordField('пароль', validators=[DataRequired()])
    remember_me = BooleanField('запомнить меня')
    submit = SubmitField('войти')


class RegistrationForm(FlaskForm):
    username = StringField('username', validators=[
        DataRequired(), Length(1, 64), Regexp('^[a-z][a-z0-9_]*$', 0, 'only letters, digits and underscores')])
    email = StringField('email', validators=[DataRequired(), Length(5, 64), Email()])
    password = PasswordField('password', validators=[DataRequired()])
    password_confirm = PasswordField('confirm password', validators=[
        DataRequired(), EqualTo('password', 'passwords must match')])
    submit = SubmitField('register')

    def validate_email(self, field):
        if SystemUser.query.filter_by(email=field.data).first():
            raise ValidationError('email already registered!')

    def validate_username(self, field):
        if SystemUser.query.filter_by(username=field.data).first():
            raise ValidationError('username already registered!')
