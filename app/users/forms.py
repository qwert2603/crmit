from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, ValidationError, SelectField, Label, \
    SelectMultipleField, TextAreaField
from wtforms.validators import Length, DataRequired, EqualTo, Regexp, Optional, Email

from app.form import DateFieldWidget, VkLink, Phone, prefix_field_required
from app.models import SystemUser, School, Citizenship, Parent, notification_types_list, shift_email, shift_vk, \
    contact_phone_variants, contact_phone_student, contact_phone_mother, contact_phone_father
from app.utils import notification_types_list_to_int


class LoginForm(FlaskForm):
    login = StringField('логин', validators=[Length(1, 64)])
    password = PasswordField('пароль', validators=[DataRequired()])
    remember_me = BooleanField('запомнить меня')
    submit = SubmitField('войти')


class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(prefix_field_required + 'текущий пароль', validators=[DataRequired()])
    new_password = PasswordField(prefix_field_required + 'новый пароль', validators=[Length(1, 255)])
    new_password_confirm = PasswordField(prefix_field_required + 'подтверждение нового пароля', validators=[
        DataRequired(), EqualTo('new_password', 'пароли должны совпадать')])
    submit = SubmitField('изменить пароль')


class ForceChangePasswordForm(FlaskForm):
    new_password = PasswordField(prefix_field_required + 'новый пароль', validators=[Length(1, 255)])
    new_password_confirm = PasswordField(prefix_field_required + 'подтверждение нового пароля', validators=[
        DataRequired(), EqualTo('new_password', 'пароли должны совпадать')])
    submit = SubmitField('изменить пароль')


# base field for registration.
class RegistrationForm(FlaskForm):
    login = StringField(prefix_field_required + 'логин',
                        validators=[Length(1, 64),
                                    Regexp('^[a-z][a-z0-9_]*$', 0, 'только буквы / цифры / подчеркивание')])
    fio = StringField(prefix_field_required + 'фио', validators=[Length(1, 255)])
    password = PasswordField(prefix_field_required + 'пароль', validators=[Length(1, 255)])
    password_confirm = PasswordField(prefix_field_required + 'подтверждение пароля', validators=[
        DataRequired(), EqualTo('password', 'пароли должны совпадать')])
    enabled = BooleanField('включен', default=True)

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
    submit = SubmitField('создать руководителя')

    def __init__(self, master=None, *args, **kwargs):
        super(RegistrationMasterForm, self).__init__(*args, **kwargs)
        self.master = master
        if master is not None:
            self.system_user = master.system_user
            self.setup_for_editing()


class RegistrationTeacherForm(RegistrationForm):
    phone = StringField(prefix_field_required + 'телефон', validators=[Phone(allow_empty=False)])
    submit = SubmitField('создать преподавателя')

    def __init__(self, teacher=None, *args, **kwargs):
        super(RegistrationTeacherForm, self).__init__(*args, **kwargs)
        self.teacher = teacher
        if teacher is not None:
            self.system_user = teacher.system_user
            self.setup_for_editing()


class RegistrationBotForm(RegistrationForm):
    submit = SubmitField('создать бота')

    def __init__(self, bot=None, *args, **kwargs):
        super(RegistrationBotForm, self).__init__(*args, **kwargs)
        self.bot = bot
        self.fio.label = Label(self.fio.id, prefix_field_required + "имя")
        if bot is not None:
            self.system_user = bot.system_user
            self.setup_for_editing()


class RegistrationDeveloperForm(RegistrationForm):
    submit = SubmitField('создать разработчика')

    def __init__(self, developer=None, *args, **kwargs):
        super(RegistrationDeveloperForm, self).__init__(*args, **kwargs)
        self.developer = developer
        if developer is not None:
            self.system_user = developer.system_user
            self.setup_for_editing()


no_parent_id = -1
create_new_parent_id = -2


class RegistrationStudentForm(RegistrationForm):
    last_name = StringField(prefix_field_required + 'фамилия', validators=[Length(1, 60)])
    first_name = StringField(prefix_field_required + 'имя', validators=[Length(1, 60)])
    second_name = StringField('отчество', validators=[Length(0, 60)])
    birth_date = DateFieldWidget(prefix_field_required + 'дата рождения', validators=[DataRequired()])
    birth_place = StringField(prefix_field_required + 'место рождения', validators=[Length(1, 255)])
    registration_place = StringField(prefix_field_required + 'адрес регистрации', validators=[Length(1, 255)])
    actual_address = StringField(prefix_field_required + 'фактический адрес проживания', validators=[Length(1, 255)])
    additional_info = TextAreaField('дополнительная информация', validators=[Length(0, 255)])
    known_from = StringField('откуда узнал(а) о ЦМИТ', validators=[Length(0, 255)])
    citizenship = SelectField(prefix_field_required + 'гражданство', coerce=int, validators=[DataRequired()])
    school = SelectField(prefix_field_required + 'школа', coerce=int, validators=[DataRequired()])
    grade = StringField(prefix_field_required + 'класс', validators=[Length(1, 31)])
    shift = StringField(prefix_field_required + 'смена', validators=[Length(1, 31)])
    phone = StringField('телефон', validators=[Phone(allow_empty=True)])
    contact_phone = SelectField(prefix_field_required + 'телефон для связи', coerce=int, validators=[DataRequired()])
    mother_search = StringField('мать. поиск', validators=[Optional()])
    mother = SelectField('мать (при создании нового заполните поля ниже)', coerce=int, validators=[Optional()])
    father_search = StringField('отец. поиск', validators=[Optional()])
    father = SelectField('отец (при создании нового заполните поля ниже)', coerce=int, validators=[Optional()])

    m_fio = StringField(prefix_field_required + 'новая мать: фио', validators=[Length(0, 255)])
    m_phone = StringField(prefix_field_required + 'новая мать: телефон', validators=[Phone(allow_empty=True)])
    m_email = StringField('новая мать: email', validators=[Optional(), Length(0, 128), Email()])
    m_passport = StringField('новая мать: паспорт', validators=[Optional(), Length(0, 255)])
    m_address = StringField('новая мать: адрес', validators=[Optional(), Length(0, 255)])
    m_home_phone = StringField('новая мать: домашний телефон', validators=[Length(0, 32)])
    m_vk_link = StringField('новая мать: ВКонтакте', validators=[Optional(), Length(0, 64), VkLink()])
    m_notification_types = SelectMultipleField('новая мать: уведомления', coerce=int, validators=[Optional()])

    f_fio = StringField(prefix_field_required + 'новый отец: фио', validators=[Length(0, 255)])
    f_phone = StringField(prefix_field_required + 'новый отец: телефон', validators=[Phone(allow_empty=True)])
    f_email = StringField('новый отец: email', validators=[Optional(), Length(0, 128), Email()])
    f_passport = StringField('новый отец: паспорт', validators=[Optional(), Length(0, 255)])
    f_address = StringField('новый отец: адрес', validators=[Optional(), Length(0, 255)])
    f_home_phone = StringField('новый отец: домашний телефон', validators=[Length(0, 32)])
    f_vk_link = StringField('новый отец: ВКонтакте', validators=[Optional(), Length(0, 64), VkLink()])
    f_notification_types = SelectMultipleField('новый отец: уведомления', coerce=int, validators=[Optional()])

    def required_fields_values_new_mother(self):
        return [self.m_fio.data, self.m_phone.data]

    def required_fields_values_new_father(self):
        return [self.f_fio.data, self.f_phone.data]

    submit = SubmitField('создать ученика')

    def __init__(self, student=None, *args, **kwargs):
        super(RegistrationStudentForm, self).__init__(*args, *kwargs)

        schools = [(school.id, school.name) for school in School.query.order_by(School.name).all()]
        if student is None:
            schools = [(-1, 'выберите школу')] + schools
        self.school.choices = schools

        self.contact_phone.choices = contact_phone_variants
        self.citizenship.choices = [(c.id, c.name) for c in Citizenship.query.order_by(Citizenship.id).all()]

        parents = [(p.id, p.fio) for p in Parent.query.order_by(Parent.fio).all()]
        parents = [(create_new_parent_id, 'создать нового')] + parents
        parents = [(no_parent_id, 'нет')] + parents
        self.mother.choices = parents
        self.father.choices = parents

        self.m_notification_types.choices = [[no_parent_id, 'нет']] + notification_types_list
        self.f_notification_types.choices = [[no_parent_id, 'нет']] + notification_types_list

        self.student = student
        if student is not None:
            del self.last_name
            del self.first_name
            del self.second_name
            self.setup_for_editing()
            self.system_user = student.system_user
        else:
            # this fields are generated from last_name / first_name / second_name.
            del self.login
            del self.fio
            del self.password
            del self.password_confirm

    def validate_school(self, field):
        if field.data <= 0:
            raise ValidationError('школа не выбрана!')

    def validate_contact_phone(self, field):
        if field.data == contact_phone_student and self.phone.data == '':
            raise ValidationError('укажите телефон ученика!')
        if field.data == contact_phone_mother and self.mother.data == no_parent_id:
            raise ValidationError('мать не указана!')
        if field.data == contact_phone_father and self.father.data == no_parent_id:
            raise ValidationError('отец не указан!')

    def validate_father(self, field):
        if field.data > 0 and field.data == self.mother.data:
            raise ValidationError('отец не может быть матерью!')
        if field.data == create_new_parent_id:
            if any(len(p) == 0 for p in self.required_fields_values_new_father()):
                raise ValidationError('заполните поля в "новый родитель - отец"!')
            # if self.f_passport.data is empty, nothing will be found because empty passport is stored in DB as NULL.
            if Parent.query.filter_by(_passport=self.f_passport.data).first():
                raise ValidationError('паспорт отца уже зарегистрирован!')
            if self.mother.data == create_new_parent_id and self.f_passport.data.strip() != '' \
                    and self.f_passport.data == self.m_passport.data:
                raise ValidationError('паспорта родителей совпадают!')

    def validate_mother(self, field):
        if field.data == create_new_parent_id:
            if any(len(p) == 0 for p in self.required_fields_values_new_mother()):
                raise ValidationError('заполните поля в "новый родитель - мать"!')
            if Parent.query.filter_by(_passport=self.m_passport.data).first():
                raise ValidationError('паспорт матери уже зарегистрирован!')

    def validate_m_notification_types(self, field):
        if self.mother.data != create_new_parent_id: return
        ni_ints = notification_types_list_to_int(field.data)
        if ni_ints & (1 << shift_email) != 0 and self.m_email.data.strip() == '':
            raise ValidationError('укажите email!')
        if ni_ints & (1 << shift_vk) != 0 and self.m_vk_link.data.strip() == '':
            raise ValidationError('укажите ВКонтакте!')
        # don't check phone here because it is required.

    def validate_f_notification_types(self, field):
        if self.father.data != create_new_parent_id: return
        ni_ints = notification_types_list_to_int(field.data)
        if ni_ints & (1 << shift_email) != 0 and self.f_email.data.strip() == '':
            raise ValidationError('укажите email!')
        if ni_ints & (1 << shift_vk) != 0 and self.f_vk_link.data.strip() == '':
            raise ValidationError('укажите ВКонтакте!')
        # don't check phone here because it is required.


class RegistrationStudentFastForm(FlaskForm):
    last_name = StringField(prefix_field_required + 'фамилия', validators=[Length(1, 60)])
    first_name = StringField(prefix_field_required + 'имя', validators=[Length(1, 60)])
    second_name = StringField('отчество', validators=[Length(0, 60)])
    birth_date = DateFieldWidget(prefix_field_required + 'дата рождения', validators=[DataRequired()])
    school = SelectField(prefix_field_required + 'школа', coerce=int, validators=[DataRequired()])
    grade = StringField(prefix_field_required + 'класс', validators=[Length(1, 31)])
    shift = StringField(prefix_field_required + 'смена', validators=[Length(1, 31)])
    parent_name = StringField(prefix_field_required + 'имя родителя', validators=[Length(1, 31)])
    parent_phone = StringField(prefix_field_required + 'телефон родителя', validators=[Length(1, 31)])
    submit = SubmitField('создать ученика')

    def __init__(self, *args, **kwargs):
        super(RegistrationStudentFastForm, self).__init__(*args, *kwargs)
        schools = [(school.id, school.name) for school in School.query.order_by(School.name).all()]
        schools = [(-1, 'выберите школу')] + schools
        self.school.choices = schools

    def validate_school(self, field):
        if field.data <= 0:
            raise ValidationError('школа не выбрана!')
