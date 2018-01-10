from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError, DateField, SelectField
from wtforms.validators import Length, DataRequired, EqualTo, Regexp, Optional

from app.models import SystemUser, School, Citizenship, Parent


class LoginForm(FlaskForm):
    login = StringField('логин', validators=[Length(1, 64)])
    password = PasswordField('пароль', validators=[DataRequired()])
    remember_me = BooleanField('запомнить меня')
    submit = SubmitField('войти')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField('текущий пароль', validators=[DataRequired()])
    new_password = PasswordField('новый пароль', validators=[Length(1, 255)])
    new_password_confirm = PasswordField('подтверждение нового пароля', validators=[
        DataRequired(), EqualTo('new_password', 'пароли должны совпадать')])
    submit = SubmitField('изменить пароль')


# base field for registration.
class RegistrationForm(FlaskForm):
    login = StringField('логин', validators=[Length(1, 64),
                                             Regexp('^[a-z][a-z0-9_]*$', 0, 'только буквы / цифры / подчеркивание')])
    fio = StringField('фио', validators=[Length(1, 255), Regexp('^[а-яА-Я ]*$', 0, 'только русские буквы')])
    password = PasswordField('пароль', validators=[Length(1, 255)])
    password_confirm = PasswordField('подтверждение пароля', validators=[
        DataRequired(), EqualTo('password', 'пароли должны совпадать')])

    def validate_login(self, field):
        if SystemUser.query.filter_by(login=field.data).first():
            raise ValidationError('логин уже Занят!')


class RegistrationMasterForm(RegistrationForm):
    submit = SubmitField('создать мастера')


class RegistrationTeacherForm(RegistrationForm):
    submit = SubmitField('создать преподавателя')


class RegistrationStudentForm(RegistrationForm):
    birth_date = DateField('дата рождения', validators=[DataRequired()])
    birth_place = StringField('место рождения', validators=[Length(1, 255)])
    registration_place = StringField('адрес регистрации', validators=[Length(1, 255)])
    actual_address = StringField('фактический адрес проживания', validators=[Length(1, 255)])
    additional_info = StringField('дополнительная информация', validators=[Length(0, 255)])
    known_from = StringField('откуда узнал(а) о ЦМИТ', validators=[Length(0, 255)])
    school = SelectField('школа', coerce=int, validators=[DataRequired()])
    citizenship = SelectField('гражданство', coerce=int, validators=[DataRequired()])
    mother = SelectField('мать', coerce=int, validators=[Optional()])
    father = SelectField('отец', coerce=int, validators=[Optional()])
    submit = SubmitField('создать ученика')

    def __init__(self, *args, **kwargs):
        super(RegistrationStudentForm, self).__init__(*args, *kwargs)
        self.school.choices = [(school.id, school.name) for school in School.query.order_by(School.name).all()]
        self.citizenship.choices = [(c.id, c.name) for c in Citizenship.query.order_by(Citizenship.name).all()]
        self.mother.choices = [(p.id, p.fio) for p in Parent.query.order_by(Parent.fio).all()]
        self.father.choices = [(p.id, p.fio) for p in Parent.query.order_by(Parent.fio).all()]
