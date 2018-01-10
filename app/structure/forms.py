from flask_wtf import FlaskForm
from wtforms import StringField, ValidationError, IntegerField, SelectField
from wtforms.validators import Length, DataRequired, Email, Regexp
from models import Group, Section, Citizenship, School, Parent


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
