from datetime import datetime
from flask_login import AnonymousUserMixin, UserMixin
from sqlalchemy import or_
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.utils import end_date_of_month, start_date_of_month


class AnonUser(AnonymousUserMixin):
    id = -1
    system_role = None


class SystemRole(db.Model):
    __tablename__ = 'system_roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    details_table_name = db.Column(db.String(255), nullable=False)
    system_users = db.relationship('SystemUser', backref='system_role', lazy='dynamic')


last_seen_registration = 1
last_seen_web = 2
last_seen_android = 3


class SystemUser(UserMixin, db.Model):
    __tablename__ = 'system_users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False, unique=True)
    system_role_id = db.Column(db.Integer, db.ForeignKey('system_roles.id'), nullable=False)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_seen_where = db.Column(db.Integer, default=last_seen_registration, nullable=False)
    enabled = db.Column(db.Boolean, nullable=False)
    master = db.relationship('Master', backref='system_user', uselist=False)
    teacher = db.relationship('Teacher', backref='system_user', uselist=False)
    student = db.relationship('Student', backref='system_user', uselist=False)
    notifications = db.relationship('Notification', backref='sender', lazy='dynamic')
    access_tokens = db.relationship('AccessToken', backref='system_user', lazy='dynamic')

    @property
    def details(self):
        if self.system_role.details_table_name == Master.__tablename__: return self.master
        if self.system_role.details_table_name == Teacher.__tablename__: return self.teacher
        if self.system_role.details_table_name == Student.__tablename__: return self.student

    @property
    def password(self):
        raise AttributeError('password is not for reading.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def access_tokens_not_expired(self):
        return self.access_tokens.filter(AccessToken.expires > datetime.utcnow())

    def access_tokens_expired(self):
        return self.access_tokens.filter(AccessToken.expires < datetime.utcnow())


class School(db.Model):
    __tablename__ = 'schools'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    students = db.relationship('Student', backref='school', lazy='dynamic')


class Citizenship(db.Model):
    __tablename__ = 'citizenships'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    students = db.relationship('Student', backref='citizenship', lazy='dynamic')


shift_email = 0
shift_vk = 1
shift_sms = 2
notification_types_list = [
    [shift_email, 'email'],
    [shift_vk, 'ВКонтакте'],
    [shift_sms, 'sms']
]

vk_link_prefix = 'vk.com/'


class Parent(db.Model):
    __tablename__ = 'parents'
    id = db.Column(db.Integer, primary_key=True)
    fio = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(255), nullable=False)
    _email = db.Column(db.String(255), name='email', nullable=True)
    _passport = db.Column(db.String(255), name='passport', nullable=True, unique=True)
    _address = db.Column(db.String(255), name='address', nullable=True)
    _home_phone = db.Column(db.String(255), name='home_phone', nullable=True)
    _vk_link = db.Column(db.String(255), name='vk_link', nullable=True)
    notification_types = db.Column(db.Integer, nullable=False)
    parent_of_students = db.relationship('ParentOfStudent', backref='parent', lazy='dynamic')

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, new_email):
        new_email = new_email.strip()
        if new_email != '':
            self._email = new_email
        else:
            self._email = None

    @property
    def vk_link(self):
        return self._vk_link

    @vk_link.setter
    def vk_link(self, new_vk_link):
        new_vk_link = new_vk_link.strip()
        if new_vk_link != '':
            self._vk_link = new_vk_link
        else:
            self._vk_link = None

    @property
    def home_phone(self):
        return self._home_phone

    @home_phone.setter
    def home_phone(self, new_home_phone):
        new_home_phone = new_home_phone.strip()
        if new_home_phone != '':
            self._home_phone = new_home_phone
        else:
            self._home_phone = None

    @property
    def passport(self):
        return self._passport

    @passport.setter
    def passport(self, new_passport):
        new_passport = new_passport.strip()
        if new_passport != '':
            self._passport = new_passport
        else:
            self._passport = None

    @property
    def address(self):
        return self._address

    @address.setter
    def address(self, new_address):
        new_address = new_address.strip()
        if new_address != '':
            self._address = new_address
        else:
            self._address = None

    @property
    def children(self):
        return Student.query \
            .join(ParentOfStudent, ParentOfStudent.student_id == Student.id) \
            .filter(ParentOfStudent.parent_id == self.id)

    @property
    def notification_types_string(self):
        result = list()
        for nt in notification_types_list:
            if self.notification_types & (1 << nt[0]) != 0:
                result.append(nt[1])
        return result


contact_phone_student = 1
contact_phone_mother = 2
contact_phone_father = 3

contact_phone_variants = [
    [contact_phone_student, 'телефон ученика'],
    [contact_phone_mother, 'телефон матери'],
    [contact_phone_father, 'телефон отца']
]


class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    fio = db.Column(db.String(255), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    birth_place = db.Column(db.String(255), nullable=False)
    registration_place = db.Column(db.String(255), nullable=False)
    actual_address = db.Column(db.String(255), nullable=False)
    additional_info = db.Column(db.Text, nullable=True)
    known_from = db.Column(db.Text, nullable=True)
    school_id = db.Column(db.Integer, db.ForeignKey('schools.id'), nullable=False)
    citizenship_id = db.Column(db.Integer, db.ForeignKey('citizenships.id'), nullable=False)
    system_user_id = db.Column(db.Integer, db.ForeignKey('system_users.id'), nullable=False, unique=True)
    grade = db.Column(db.String(32), nullable=False)
    shift = db.Column(db.String(32), nullable=False)
    _phone = db.Column(db.String(255), name='phone', nullable=True)
    contact_phone = db.Column(db.Integer, nullable=False)
    filled = db.Column(db.Boolean, nullable=False, default=True)
    students_in_groups = db.relationship('StudentInGroup', backref='student', lazy='dynamic')
    attendings = db.relationship('Attending', backref='student', lazy='dynamic')
    parent_of_students = db.relationship('ParentOfStudent', backref='student', lazy='dynamic')

    @property
    def phone(self):
        return self._phone

    @phone.setter
    def phone(self, new_phone):
        new_phone = new_phone.strip()
        if new_phone != '':
            self._phone = new_phone
        else:
            self._phone = None

    @property
    def parents(self):
        return Parent.query \
            .join(ParentOfStudent, ParentOfStudent.parent_id == Parent.id) \
            .filter(ParentOfStudent.student_id == self.id)

    @property
    def mother(self):
        return Parent.query \
            .join(ParentOfStudent, ParentOfStudent.parent_id == Parent.id) \
            .filter(ParentOfStudent.student_id == self.id, ParentOfStudent.is_mother == True) \
            .first()

    @property
    def father(self):
        return Parent.query \
            .join(ParentOfStudent, ParentOfStudent.parent_id == Parent.id) \
            .filter(ParentOfStudent.student_id == self.id, ParentOfStudent.is_mother == False) \
            .first()

    @property
    def groups(self):
        return Group.query \
            .join(StudentInGroup, StudentInGroup.group_id == Group.id) \
            .filter(StudentInGroup.student_id == self.id)

    @property
    def contact_phone_number(self):
        if self.contact_phone == contact_phone_student:
            return self.phone
        elif self.contact_phone == contact_phone_mother:
            return self.mother.phone
        elif self.contact_phone == contact_phone_father:
            return self.father.phone

    @property
    def contact_phone_who(self):
        if self.contact_phone == contact_phone_student:
            return 'ученик'
        elif self.contact_phone == contact_phone_mother:
            return 'мать'
        elif self.contact_phone == contact_phone_father:
            return 'отец'


class ParentOfStudent(db.Model):
    __tablename__ = 'parent_of_students'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=False)
    is_mother = db.Column(db.Boolean, nullable=False)
    unique = db.UniqueConstraint(student_id, parent_id, is_mother)
    unique_2 = db.UniqueConstraint(student_id, parent_id)
    unique_3 = db.UniqueConstraint(student_id, is_mother)

    @staticmethod
    def change_parent(student_id, old_parent_id, new_parent_id, is_mother):
        pos = ParentOfStudent.query.filter(
            ParentOfStudent.parent_id == old_parent_id,
            ParentOfStudent.student_id == student_id,
            ParentOfStudent.is_mother == is_mother).first()
        if pos:
            if new_parent_id:
                pos.parent_id = new_parent_id
            else:
                db.session.delete(pos)
        else:
            if new_parent_id:
                db.session.add(ParentOfStudent(parent_id=new_parent_id, student_id=student_id, is_mother=is_mother))
            else:
                pass


class Master(db.Model):
    __tablename__ = 'masters'
    id = db.Column(db.Integer, primary_key=True)
    fio = db.Column(db.String(255), nullable=False)
    system_user_id = db.Column(db.Integer, db.ForeignKey('system_users.id'), nullable=False, unique=True)


class Teacher(db.Model):
    __tablename__ = 'teachers'
    id = db.Column(db.Integer, primary_key=True)
    fio = db.Column(db.String(255), nullable=False)
    system_user_id = db.Column(db.Integer, db.ForeignKey('system_users.id'), nullable=False, unique=True)
    phone = db.Column(db.String(255), nullable=False)
    groups = db.relationship('Group', backref='teacher', lazy='dynamic')
    lessons = db.relationship('Lesson', backref='teacher', lazy='dynamic')


class Section(db.Model):
    __tablename__ = 'sections'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    price = db.Column(db.Integer, nullable=False)
    groups = db.relationship('Group', backref='section', lazy='dynamic')
    section_preferences = db.relationship('SectionPreference', backref='section', lazy='dynamic')


class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    start_month = db.Column(db.Integer, nullable=False, index=True)
    end_month = db.Column(db.Integer, nullable=False, index=True)
    students_in_group = db.relationship('StudentInGroup', backref='group', lazy='dynamic')
    lessons = db.relationship('Lesson', backref='group', lazy='dynamic')
    schedule_groups = db.relationship('ScheduleGroup', backref='group', lazy='dynamic')

    @property
    def students(self):
        return Student.query \
            .join(StudentInGroup, StudentInGroup.student_id == Student.id) \
            .filter(StudentInGroup.group_id == self.id)

    @property
    def parents(self):
        return Parent.query \
            .join(ParentOfStudent, ParentOfStudent.parent_id == Parent.id) \
            .join(StudentInGroup, StudentInGroup.student_id == ParentOfStudent.student_id) \
            .filter(StudentInGroup.group_id == self.id)

    def students_in_month(self, month_number):
        return self.students.filter(StudentInGroup.enter_month <= month_number,
                                    StudentInGroup.exit_month >= month_number)

    def students_in_group_in_month(self, month_number):
        return self.students_in_group.filter(StudentInGroup.enter_month <= month_number,
                                             StudentInGroup.exit_month >= month_number)

    @property
    def notifications(self):
        return Notification.query.filter(Notification.receiver_type == receiver_type_group,
                                         Notification.receiver_id == self.id)


class StudentInGroup(db.Model):
    __tablename__ = 'student_in_groups'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False, index=True)
    discount = db.Column(db.Integer, nullable=False, default=0)
    enter_month = db.Column(db.Integer, nullable=False, index=True)
    exit_month = db.Column(db.Integer, nullable=False, index=True)
    payments = db.relationship('Payment', backref='student_in_group', lazy='dynamic')
    unique = db.UniqueConstraint(student_id, group_id)

    @property
    def attendings(self):
        return Attending.query \
            .join(Lesson, Lesson.id == Attending.lesson_id) \
            .filter(Lesson.group_id == self.group_id, Attending.student_id == self.student_id)

    @property
    def attendings_was(self):
        return self.attendings.filter(Attending.state == attending_was)

    @property
    def attendings_was_not(self):
        return self.attendings \
            .filter(or_(Attending.state == attending_was_not, Attending.state == attending_was_not_ill))

    @property
    def payments_confirmed(self):
        return self.payments.filter(Payment.confirmed == True)

    @property
    def payments_not_confirmed(self):
        return self.payments.filter(Payment.confirmed == False)

    @property
    def max_enter_month_number(self):
        from app.structure.utils import max_enter_month_number_student_in_group
        return max_enter_month_number_student_in_group(self)

    @property
    def min_exit_month_number(self):
        from app.structure.utils import min_exit_month_number_student_in_group
        return min_exit_month_number_student_in_group(self)

    @property
    def notifications(self):
        return Notification.query.filter(Notification.receiver_type == receiver_type_student_in_group,
                                         Notification.receiver_id == self.id)


class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    student_in_group_id = db.Column(db.Integer, db.ForeignKey('student_in_groups.id'), nullable=False, index=True)
    month = db.Column(db.Integer, nullable=False, index=True)
    value = db.Column(db.Integer, nullable=False)
    cash = db.Column(db.Boolean, nullable=False, default=True)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    comment = db.Column(db.String(32), nullable=False)
    unique = db.UniqueConstraint(student_in_group_id, month)


class Lesson(db.Model):
    __tablename__ = 'lessons'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, index=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False, index=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False, index=True)
    attendings = db.relationship('Attending', backref='lesson', lazy='dynamic')

    @property
    def attendings_was(self):
        return self.attendings.filter(Attending.state == attending_was)

    @property
    def attendings_was_not(self):
        return self.attendings \
            .filter(or_(Attending.state == attending_was_not, Attending.state == attending_was_not_ill))

    @staticmethod
    def lessons_in_group_in_month(group_id, month_number):
        return Lesson.query.filter(Lesson.group_id == group_id,
                                   Lesson.date >= start_date_of_month(month_number),
                                   Lesson.date <= end_date_of_month(month_number))


attending_was_not = 0
attending_was = 1
attending_was_not_ill = 2

attending_states = [
    attending_was_not,
    attending_was,
    attending_was_not_ill
]


class Attending(db.Model):
    __tablename__ = 'attendings'
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False, index=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False, index=True)
    state = db.Column(db.Integer, nullable=False)
    unique = db.UniqueConstraint(student_id, lesson_id)


receiver_type_group = 1
receiver_type_student_in_group = 2


class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('system_users.id'), nullable=False, index=True)
    receiver_type = db.Column(db.Integer, nullable=False, index=True)
    receiver_id = db.Column(db.Integer, nullable=False, index=True)
    subject = db.Column(db.Text, nullable=False)
    body = db.Column(db.Text, nullable=False)
    send_time = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    receivers = db.Column(db.Text, nullable=False)

    @property
    def group(self):
        if self.receiver_type == receiver_type_group:
            return Group.query.get(self.receiver_id)

    @property
    def student_in_group(self):
        if self.receiver_type == receiver_type_student_in_group:
            return StudentInGroup.query.get(self.receiver_id)

    @property
    def receivers_html(self):
        return '<ul>' + ''.join(['<li>{}</li>'.format(s) for s in self.receivers.split()]) + '</ul>'


class Candidate(db.Model):
    __tablename__ = 'candidates'
    id = db.Column(db.Integer, primary_key=True)
    fio = db.Column(db.String(255), nullable=False)
    shift = db.Column(db.Integer, nullable=False)
    section_preferences = db.relationship('SectionPreference', backref='candidate', lazy='dynamic')
    day_preferences = db.relationship('DayPreference', backref='candidate', lazy='dynamic')


class SectionPreference(db.Model):
    __tablename__ = 'section_preferences'
    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)
    unique = db.UniqueConstraint(candidate_id, section_id)


class DayPreference(db.Model):
    __tablename__ = 'day_preferences'
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Integer, nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)
    unique = db.UniqueConstraint(candidate_id, day)


class ScheduleTime(db.Model):
    __tablename__ = 'schedule_times'
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.String(8), nullable=True)
    schedule_groups = db.relationship('ScheduleGroup', backref='schedule_time', lazy='dynamic')


class ScheduleGroup(db.Model):
    __tablename__ = 'schedule_groups'
    id = db.Column(db.Integer, primary_key=True)
    schedule_time_id = db.Column(db.Integer, db.ForeignKey('schedule_times.id'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=True)
    unique = db.UniqueConstraint(schedule_time_id, day_of_week)


class AccessToken(db.Model):
    __tablename__ = 'access_tokens'
    id = db.Column(db.Integer, primary_key=True)
    token_hash = db.Column(db.String(255), nullable=False)
    system_user_id = db.Column(db.Integer, db.ForeignKey('system_users.id'), nullable=False)
    expires = db.Column(db.DateTime, nullable=False)
