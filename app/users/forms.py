from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError, SelectField, Label, \
    SelectMultipleField
from wtforms.validators import Length, DataRequired, EqualTo, Regexp, Optional, Email

from app.form import DateFieldWidget, VkLink
from app.models import SystemUser, School, Citizenship, Parent, notification_types_list, shift_email, shift_vk
from app.utils import notification_types_list_to_int


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

    system_user = None

    def validate_login(self, field):
        if (self.system_user is None or self.system_user.login != field.data) \
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


no_parent_id = -1
create_new_parent_id = -2


class RegistrationStudentForm(RegistrationForm):
    last_name = StringField('фамилия', validators=[Length(1, 60), Regexp('^[А-Я][а-я]+$', 0, 'только русские буквы')])
    first_name = StringField('имя', validators=[Length(1, 60), Regexp('^[А-Я][а-я]+$', 0, 'только русские буквы')])
    second_name = StringField('отчество',
                              validators=[Length(0, 60), Regexp('^[А-Я][а-я]+$|^$', 0, 'только русские буквы')])
    birth_date = DateFieldWidget('дата рождения', validators=[DataRequired()])
    birth_place = StringField('место рождения', validators=[Length(1, 255)])
    registration_place = StringField('адрес регистрации', validators=[Length(1, 255)])
    actual_address = StringField('фактический адрес проживания', validators=[Length(1, 255)])
    additional_info = StringField('дополнительная информация', validators=[Length(0, 255)])
    known_from = StringField('откуда узнал(а) о ЦМИТ', validators=[Length(0, 255)])
    school = SelectField('школа', coerce=int, validators=[DataRequired()])
    citizenship = SelectField('гражданство', coerce=int, validators=[DataRequired()])
    mother = SelectField('мать', coerce=int, validators=[Optional()])
    father = SelectField('отец', coerce=int, validators=[Optional()])

    m_fio = StringField('новая мать: фио',
                        validators=[Length(0, 255), Regexp('^[а-яА-Я ]*$', 0, 'только русские буквы')])
    m_phone = StringField('новая мать: телефон', validators=[Length(0, 32)])
    m_email = StringField('новая мать: email', validators=[Optional(), Length(0, 128), Email()])
    m_passport = StringField('новая мать: паспорт', validators=[Length(0, 255)])
    m_address = StringField('новая мать: адрес', validators=[Length(0, 255)])
    m_home_phone = StringField('новая мать: домашний телефон', validators=[Length(0, 32)])
    m_vk_link = StringField('новая мать: ВКонтакте', validators=[Optional(), Length(0, 64), VkLink()])
    m_notification_types = SelectMultipleField('новая мать: уведомления', coerce=int, validators=[Optional()])

    f_fio = StringField('новый отец: фио',
                        validators=[Length(0, 255), Regexp('^[а-яА-Я ]*$', 0, 'только русские буквы')])
    f_phone = StringField('новый отец: телефон', validators=[Length(0, 32)])
    f_email = StringField('новый отец: email', validators=[Optional(), Length(0, 128), Email()])
    f_passport = StringField('новый отец: паспорт', validators=[Length(0, 255)])
    f_address = StringField('новый отец: адрес', validators=[Length(0, 255)])
    f_home_phone = StringField('новый отец: домашний телефон', validators=[Length(0, 32)])
    f_vk_link = StringField('новый отец: ВКонтакте', validators=[Optional(), Length(0, 64), VkLink()])
    f_notification_types = SelectMultipleField('новый отец: уведомления', coerce=int, validators=[Optional()])

    def required_fields_values_new_mother(self):
        return [self.m_fio.data, self.m_phone.data, self.m_passport.data, self.m_address.data]

    def required_fields_values_new_father(self):
        return [self.f_fio.data, self.f_phone.data, self.f_passport.data, self.f_address.data]

    submit = SubmitField('создать ученика')

    def __init__(self, student=None, *args, **kwargs):
        super(RegistrationStudentForm, self).__init__(*args, *kwargs)
        schools = [(school.id, school.name) for school in School.query.order_by(School.name).all()]
        if student is None:
            schools = [(-1, 'выберите школу')] + schools
        self.school.choices = schools
        self.citizenship.choices = [(c.id, c.name) for c in Citizenship.query.order_by(Citizenship.id).all()]
        parents = [(no_parent_id, 'нет')] + [(p.id, p.fio) for p in Parent.query.order_by(Parent.fio).all()]
        if student is None:
            parents = [(create_new_parent_id, 'создать нового')] + parents
        self.mother.choices = parents
        self.father.choices = parents

        self.student = student
        if student is not None:
            del self.last_name
            del self.first_name
            del self.second_name
            self.setup_for_editing()
            self.system_user = student.system_user
            self.delete_new_parents_fields()
        else:
            # this fields are generated from last_name / first_name / second_name.
            del self.login
            del self.fio
            del self.password
            del self.password_confirm
            self.m_notification_types.choices = [[-1, 'нет']] + notification_types_list
            self.f_notification_types.choices = [[-1, 'нет']] + notification_types_list

    def validate_school(self, field):
        if field.data <= 0:
            raise ValidationError('школа не выбрана!')

    def validate_father(self, field):
        if field.data > 0 and field.data == self.mother.data:
            raise ValidationError('отец не может быть матерью!')
        if field.data == create_new_parent_id:
            if any(len(p) == 0 for p in self.required_fields_values_new_father()):
                raise ValidationError('заполните поля в "новый родитель - отец"!')
            if Parent.query.filter_by(passport=self.f_passport.data).first():
                raise ValidationError('паспорт отца уже зарегистрирован!')
            if self.f_passport.data == self.m_passport.data:
                raise ValidationError('паспорта родителей совпадают!')

    def validate_mother(self, field):
        if field.data == create_new_parent_id:
            if any(len(p) == 0 for p in self.required_fields_values_new_mother()):
                raise ValidationError('заполните поля в "новый родитель - мать"!')
            if Parent.query.filter_by(passport=self.m_passport.data).first():
                raise ValidationError('паспорт матери уже зарегистрирован!')

    def validate_m_notification_types(self, field):
        if self.mother.data != create_new_parent_id: return
        ni_ints = notification_types_list_to_int(field.data)
        if ni_ints & (1 << shift_email) != 0 and self.m_email.data.strip() == '': raise ValidationError('укажите email!')
        if ni_ints & (1 << shift_vk) != 0 and self.m_vk_link.data.strip() == '': raise ValidationError('укажите ВКонтакте!')
        # don't check phone here because it is required.

    def validate_f_notification_types(self, field):
        if self.father.data != create_new_parent_id: return
        ni_ints = notification_types_list_to_int(field.data)
        if ni_ints & (1 << shift_email) != 0 and self.f_email.data.strip() == '': raise ValidationError('укажите email!')
        if ni_ints & (1 << shift_vk) != 0 and self.f_vk_link.data.strip() == '': raise ValidationError('укажите ВКонтакте!')
        # don't check phone here because it is required.

    def delete_new_parents_fields(self):
        del self.m_fio
        del self.m_phone
        del self.m_email
        del self.m_passport
        del self.m_address
        del self.m_home_phone
        del self.m_vk_link
        del self.m_notification_types
        del self.f_fio
        del self.f_phone
        del self.f_email
        del self.f_passport
        del self.f_address
        del self.f_home_phone
        del self.f_vk_link
        del self.f_notification_types
