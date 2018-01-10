from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError, DateField, SelectField, \
    IntegerField
from wtforms.validators import Length, DataRequired, EqualTo, Regexp, Optional, Email

from app.models import SystemUser, School, Citizenship, Parent, Section, Group


class LoginForm(FlaskForm):
    login = StringField('логин или email', validators=[Length(1, 64)])
    password = PasswordField('пароль', validators=[DataRequired()])
    remember_me = BooleanField('запомнить меня')
    submit = SubmitField('войти')


# base field for registration.
class RegistrationForm(FlaskForm):
    login = StringField('логин', validators=[Length(1, 64),
                                             Regexp('^[a-z][a-z0-9_]*$', 0, 'только буквы / цифры / подчеркивание')])
    fio = StringField('фио', validators=[Length(1, 255), Regexp('^[а-яА-Я]*$', 0, 'только русские буквы')])
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
        self.citizenship.choices = [(c.id, c.name) for c in Citizenship.query.order_by(School.name).all()]


class ParentForm(FlaskForm):
    fio = StringField('фио', validators=[Length(1, 255), Regexp('^[а-яА-Я]*$', 0, 'только русские буквы')])
    phone = StringField('телефон', validators=[Length(1, 32)])
    email = StringField('email', validators=[DataRequired(), Email()])
    passport = StringField('паспорт', validators=[Length(1, 255)])
    address = StringField('адрес', validators=[Length(1, 255)])
    home_phone = StringField('домашний телефон', validators=[Length(0, 32)])

    def validate_passport(self, field):
        if Parent.query.filter_by(passport=field.data).first():
            raise ValidationError('этот паспорт уже зарегистрирован!')


class SchoolForm(FlaskForm):
    name = StringField('название школы', validators=[Length(1, 255)])

    def validate_name(self, field):
        if School.query.filter_by(name=field.data).first():
            raise ValidationError('школа с Таким названием уже существует!')


class CitizenshipForm(FlaskForm):
    name = StringField('гражданство', validators=[Length(1, 255)])

    def validate_name(self, field):
        if Citizenship.query.filter_by(name=field.data).first():
            raise ValidationError('гражданство с Таким названием уже существует!')


class SectionForm(FlaskForm):
    name = StringField('название секции', validators=[Length(1, 255)])
    price = IntegerField('цена за месяц', validators=[DataRequired()])

    def validate_name(self, field):
        if Section.query.filter_by(name=field.data).first():
            raise ValidationError('секция с Таким названием уже существует!')

    def validate_price(self, field):
        if field.data <= 0:
            raise ValidationError('цена должна быть больше 0!')
        if field.data > 10000:
            raise ValidationError('цена слишком БОЛЬШАЯ!')


class GroupForm(FlaskForm):
    section = SelectField('секция', validators=[DataRequired()])
    name = StringField('название', validators=[Length(1, 255)])
    teacher = SelectField('преподаватель', validators=[DataRequired()])

    def validate_name(self, field):
        if Group.query.filter_by(name=field.data).first():
            raise ValidationError('группа с Таким названием уже существует!')
