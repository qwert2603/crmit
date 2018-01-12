from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError, DateField, SelectField, \
    Label
from wtforms.validators import Length, DataRequired, EqualTo, Regexp, Optional

from app.models import SystemUser, School, Citizenship, Parent
from app.init_model import default_citizenship_name


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
        if (self.system_user is None or field.data != self.system_user.login) \
                and SystemUser.query.filter_by(login=field.data).first():
            raise ValidationError('логин уже Занят!')

    def setup_for_editing(self):
        del self.password
        del self.password_confirm
        self.submit.label = Label(self.submit.id, 'сохранить')


class RegistrationMasterForm(RegistrationForm):
    submit = SubmitField('создать мастера')

    def __init__(self, master=None, *args, **kwargs):
        super(RegistrationMasterForm, self).__init__(*args, **kwargs)
        self.master = master
        if master is not None:
            self.system_user = master.system_user
            self.setup_for_editing()


class RegistrationTeacherForm(RegistrationForm):
    submit = SubmitField('создать преподавателя')

    def __init__(self, teacher=None, *args, **kwargs):
        super(RegistrationTeacherForm, self).__init__(*args, **kwargs)
        self.teacher = teacher
        if teacher is not None:
            self.system_user = teacher.system_user
            self.setup_for_editing()


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

    def __init__(self, student=None, *args, **kwargs):
        super(RegistrationStudentForm, self).__init__(*args, *kwargs)
        self.school.choices = [(school.id, school.name) for school in School.query.order_by(School.name).all()]
        self.citizenship.choices = [(c.id, c.name) for c in Citizenship.query.order_by(Citizenship.name).all()]
        parents = [(-1, 'нет')] + [(p.id, p.fio) for p in Parent.query.order_by(Parent.fio).all()]
        self.mother.choices = parents
        self.father.choices = parents

        self.student = student
        if student is not None:
            self.system_user = student.system_user
            self.setup_for_editing()
        else:
            self.citizenship.data = Citizenship.query.filter_by(name=default_citizenship_name).first().id

    def validate_father(self, field):
        if field.data != -1 and field.data == self.mother.data:
            raise ValidationError('отец не может быть матерью!')
