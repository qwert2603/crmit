from app import db
from app.models import SystemRole, SystemUser, Master, Teacher, Section, Group, Student, Citizenship, School, \
    StudentInGroup, Payment

role_master_name = 'руководитель'
role_teacher_name = 'преподаватель'
role_student_name = 'ученик'

default_citizenship_name = 'Россия'


def create_system_roles():
    role_master = SystemRole(name=role_master_name, details_table_name=Master.__tablename__)
    role_teacher = SystemRole(name=role_teacher_name, details_table_name=Teacher.__tablename__)
    role_student = SystemRole(name=role_student_name, details_table_name=Student.__tablename__)
    roles = [role_master, role_teacher, role_student]
    for role in roles:
        db.session.add(role)

    db.session.commit()


def create_default_citizenships():
    db.session.add(Citizenship(name=default_citizenship_name))
    db.session.add(Citizenship(name='Гражданин Мира'))
    db.session.commit()


def create_stub_models():
    create_system_roles()
    create_default_citizenships()

    role_master = SystemRole.query.filter_by(name=role_master_name).first()
    user_master = SystemUser(login='qwert2603', password='12', system_role=role_master)
    master = Master(fio='Алекс', system_user=user_master)
    db.session.add(user_master)
    db.session.add(master)

    role_teacher = SystemRole.query.filter_by(name=role_teacher_name).first()
    user_teacher = SystemUser(login='te1', password='12', system_role=role_teacher)
    teacher = Teacher(fio='учитель первый', system_user=user_teacher)
    db.session.add(user_teacher)
    db.session.add(teacher)

    school = School(name='школа №42')

    role_student = SystemRole.query.filter_by(name=role_student_name).first()
    user_student = SystemUser(login='st1', password='12', system_role=role_student)
    student = Student(fio='ученик первый', system_user=user_student, birth_place='birth place', birth_date='2002-08-31',
                      registration_place='reg place', actual_address='act addr', citizenship_id=1, school=school)
    db.session.add(user_student)
    db.session.add(student)

    section1 = Section(name='робо', price=800)
    section2 = Section(name='веб', price=900)
    db.session.add(section1)
    db.session.add(section2)

    group = Group(name='робо-71', section=section1, teacher=teacher)
    db.session.add(group)
    db.session.add(Group(name='веб-61', section=section2, teacher=teacher))

    student_in_group = StudentInGroup(student=student, group=group, discount=100, enter_month=1)
    db.session.add(student_in_group)
    db.session.add(Payment(student_in_group=student_in_group, month=1, value=800))

    db.session.commit()
