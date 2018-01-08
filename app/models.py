from flask_login import AnonymousUserMixin, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class AnonUser(AnonymousUserMixin):
    id = -1
    role = None


class SystemRole(db.Model):
    __tablename__ = 'system_roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    details_table_name = db.Column(db.String(255), nullable=False)
    system_users = db.relationship('SystemUser', backref='system_role', lazy='dynamic')


class SystemUser(UserMixin, db.Model):
    __tablename__ = 'system_users'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False, unique=True)
    system_role_id = db.Column(db.Integer, db.ForeignKey('system_roles.id'), nullable=False)

    @property
    def password(self):
        raise AttributeError('password is not for reading.')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


class School(db.Model):
    __tablename__ = 'schools'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)


class Citizenship(db.Model):
    __tablename__ = 'citizenships'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)


class Parent(db.Model):
    __tablename__ = 'parents'
    id = db.Column(db.Integer, primary_key=True)
    fio = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    passport = db.Column(db.String(255), nullable=False, unique=True)
    address = db.Column(db.String(255), nullable=False)
    home_phone = db.Column(db.String(255), nullable=True)


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
    mother_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=True)
    father_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=True)
    citizenship_id = db.Column(db.Integer, db.ForeignKey('citizenships.id'), nullable=False)
    system_user_id = db.Column(db.Integer, db.ForeignKey('system_users.id'), nullable=False, unique=True)


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


class Section(db.Model):
    __tablename__ = 'sections'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    price = db.Column(db.Integer, nullable=False)


class Group(db.Model):
    __tablename__ = 'groups'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)


class StudentInGroup(db.Model):
    __tablename__ = 'student_in_groups'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    discount = db.Column(db.Integer, nullable=True)
    enter_date = db.Column(db.Date, nullable=False)
    exit_date = db.Column(db.Date, nullable=True)


class Payment(db.Model):
    __tablename__ = 'payments'
    id = db.Column(db.Integer, primary_key=True)
    student_in_group_id = db.Column(db.Integer, db.ForeignKey('student_in_groups.id'), nullable=False)
    month = db.Column(db.Integer, nullable=False)
    value = db.Column(db.Integer, nullable=False)
    cash = db.Column(db.Boolean, nullable=False, default=True)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)


class Lesson(db.Model):
    __tablename__ = 'lessons'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)


class Attending(db.Model):
    __tablename__ = 'attendings'
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey('lessons.id'), nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    was = db.Column(db.Boolean, nullable=False, default=False)


class Candidate(db.Model):
    __tablename__ = 'candidates'
    id = db.Column(db.Integer, primary_key=True)
    fio = db.Column(db.String(255), nullable=False)
    shift = db.Column(db.Integer, nullable=False)


class SectionPreference(db.Model):
    __tablename__ = 'section_preferences'
    id = db.Column(db.Integer, primary_key=True)
    section_id = db.Column(db.Integer, db.ForeignKey('sections.id'), nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)


class DayPreference(db.Model):
    __tablename__ = 'day_preferences'
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Integer, nullable=False)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False)
