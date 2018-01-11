from flask_wtf import FlaskForm
from wtforms import StringField, ValidationError, IntegerField, SelectField, SubmitField, Label
from wtforms.validators import Length, DataRequired, Email, Regexp
from app.models import Group, Section, Citizenship, School, Parent, Teacher


class ParentForm(FlaskForm):
    fio = StringField('фио', validators=[Length(1, 255), Regexp('^[а-яА-Я ]*$', 0, 'только русские буквы')])
    phone = StringField('телефон', validators=[Length(1, 32)])
    email = StringField('email', validators=[DataRequired(), Email()])
    passport = StringField('паспорт', validators=[Length(1, 255)])
    address = StringField('адрес', validators=[Length(1, 255)])
    home_phone = StringField('домашний телефон', validators=[Length(0, 32)])
    submit = SubmitField('создать')

    def __init__(self, parent=None, *args, **kwargs):
        super(ParentForm, self).__init__(*args, **kwargs)
        self.parent = parent
        if parent is not None:
            self.submit.label = Label(self.submit.id, 'сохранить')

    def validate_passport(self, field):
        if (self.parent is None or self.passport.data != self.parent.passport) \
                and Parent.query.filter_by(passport=field.data).first():
            raise ValidationError('этот паспорт уже зарегистрирован!')


class SchoolForm(FlaskForm):
    name = StringField('название школы', validators=[Length(1, 255)])
    submit = SubmitField('создать')

    def __init__(self, school=None, *args, **kwargs):
        super(SchoolForm, self).__init__(*args, **kwargs)
        self.school = school
        if school is not None:
            self.submit.label = Label(self.submit.id, 'сохранить')

    def validate_name(self, field):
        if (self.school is None or self.name.data != self.school.name) \
                and School.query.filter_by(name=field.data).first():
            raise ValidationError('школа с Таким названием уже существует!')


class CitizenshipForm(FlaskForm):
    name = StringField('гражданство', validators=[Length(1, 255)])
    submit = SubmitField('создать')

    def __init__(self, citizenship=None, *args, **kwargs):
        super(CitizenshipForm, self).__init__(*args, **kwargs)
        self.citizenship = citizenship
        if citizenship is not None:
            self.submit.label = Label(self.submit.id, 'сохранить')

    def validate_name(self, field):
        if (self.citizenship is None or field.data != self.citizenship.name) \
                and Citizenship.query.filter_by(name=field.data).first():
            raise ValidationError('гражданство с Таким названием уже существует!')


class SectionForm(FlaskForm):
    name = StringField('название секции', validators=[Length(1, 255)])
    price = IntegerField('цена за месяц', validators=[DataRequired()])
    submit = SubmitField('создать')

    def __init__(self, section=None, *args, **kwargs):
        super(SectionForm, self).__init__(*args, **kwargs)
        self.section = section
        if section is not None:
            self.submit.label = Label(self.submit.id, 'сохранить')

    def validate_name(self, field):
        if (self.section is None or self.name.data != self.section.name) \
                and Section.query.filter_by(name=field.data).first():
            raise ValidationError('секция с Таким названием уже существует!')

    def validate_price(self, field):
        if field.data <= 0:
            raise ValidationError('цена должна быть положительной!')
        if field.data > 4000:
            raise ValidationError('цена слишком БОЛЬШАЯ!')


class GroupForm(FlaskForm):
    section = SelectField('секция', coerce=int, validators=[DataRequired()])
    name = StringField('название', validators=[Length(1, 255)])
    teacher = SelectField('преподаватель', coerce=int, validators=[DataRequired()])
    submit = SubmitField('создать')

    def __init__(self, group=None, *args, **kwargs):
        super(GroupForm, self).__init__(*args, *kwargs)
        self.section.choices = [(section.id, section.name) for section in Section.query.order_by(Section.name).all()]
        self.teacher.choices = [(teacher.id, teacher.fio) for teacher in Teacher.query.order_by(Teacher.fio).all()]
        self.group = group
        if group is not None:
            self.submit.label = Label(self.submit.id, 'сохранить')

    def validate_name(self, field):
        if (self.group is None or self.name.data != self.group.name) \
                and Group.query.filter_by(name=field.data).first():
            raise ValidationError('группа с Таким названием уже существует!')