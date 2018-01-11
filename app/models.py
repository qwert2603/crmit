from datetime import datetime
from flask_login import AnonymousUserMixin, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import db


class AnonUser(AnonymousUserMixin):
    id = -1
    system_role = None


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
    last_seen = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    master = db.relationship('Master', backref='system_user', uselist=False)
    teacher = db.relationship('Teacher', backref='system_user', uselist=False)
    student = db.relationship('Student', backref='system_user', uselist=False)

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


class Parent(db.Model):
    __tablename__ = 'parents'
    id = db.Column(db.Integer, primary_key=True)
    fio = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    passport = db.Column(db.String(255), nullable=False, unique=True)
    address = db.Column(db.String(255), nullable=False)
    home_phone = db.Column(db.String(255), nullable=True)
    parent_of_students = db.relationship('ParentOfStudent', backref='parent', lazy='dynamic')

    @property
    def children(self):
        return Student.query \
            .join(ParentOfStudent, ParentOfStudent.student_id == Student.id) \
            .filter(ParentOfStudent.parent_id == self.id)


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
    student_in_groups = db.relationship('StudentInGroup', backref='student', lazy='dynamic')
    attendings = db.relationship('Attending', backref='student', lazy='dynamic')
    parent_of_students = db.relationship('ParentOfStudent', backref='student', lazy='dynamic')

    @property
    def parents(self):
        return Parent.query \
            .join(ParentOfStudent, ParentOfStudent.parent_id == Parent.id) \
            .filter(ParentOfStudent.student_id == self.id)

    @property
    def groups(self):
        return Group.query \
            .join(StudentInGroup, StudentInGroup.group_id == Group.id) \
            .filter(StudentInGroup.student_id == self.id)


class ParentOfStudent(db.Model):
    __tablename__ = 'parent_of_students'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('parents.id'), nullable=False)
    unique = db.UniqueConstraint(student_id, parent_id)


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
    student_in_groups = db.relationship('StudentInGroup', backref='group', lazy='dynamic')
    lessons = db.relationship('Lesson', backref='group', lazy='dynamic')

    @property
    def students(self):
        return Student.query \
            .join(StudentInGroup, StudentInGroup.student_id == Student.id) \
            .filter(StudentInGroup.group_id == self.id)


class StudentInGroup(db.Model):
    __tablename__ = 'student_in_groups'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    discount = db.Column(db.Integer, nullable=True)
    enter_date = db.Column(db.Date, nullable=False)
    exit_date = db.Column(db.Date, nullable=True)
    payments = db.relationship('Payment', backref='student_in_group', lazy='dynamic')
    unique = db.UniqueConstraint(student_id, group_id)


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
    attendings = db.relationship('Attending', backref='lesson', lazy='dynamic')


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
    section_preferences = db.relationship('SectionPreference', backref='candidate', lazy='dynamic')
    day_preferences = db.relationship('DayPreference', backref='candidate', lazy='dynamic')


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
