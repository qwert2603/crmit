from app import db
from app.models import SystemRole, SystemUser, Master, Teacher, Section, Group, Student, Citizenship, School, \
    StudentInGroup, Payment, ScheduleTime, contact_phone_student, Bot

role_master_name = 'руководитель'
role_teacher_name = 'преподаватель'
role_student_name = 'ученик'
role_bot_name = 'бот'

default_citizenship_name = 'Россия'
default_citizenship_id = 1

developer_login = 'qwert2603'

actual_app_build_code = 3


def create_system_roles():
    role_master = SystemRole(name=role_master_name, details_table_name=Master.__tablename__)
    role_teacher = SystemRole(name=role_teacher_name, details_table_name=Teacher.__tablename__)
    role_student = SystemRole(name=role_student_name, details_table_name=Student.__tablename__)
    role_bot = SystemRole(name=role_bot_name, details_table_name=Bot.__tablename__)
    roles = [role_master, role_teacher, role_student, role_bot]
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
    create_schedule_times()

    role_master = SystemRole.query.filter_by(name=role_master_name).first()
    user_master = SystemUser(login='ma1', password='12', system_role=role_master, enabled=True)
    master = Master(fio='Руководитель Иван Иванович', system_user=user_master)
    db.session.add(user_master)
    db.session.add(master)

    role_teacher = SystemRole.query.filter_by(name=role_teacher_name).first()
    user_teacher = SystemUser(login='te1', password='12', system_role=role_teacher, enabled=True)
    teacher = Teacher(fio='Учитель Петр Петрович', system_user=user_teacher, phone='89012223344')
    db.session.add(user_teacher)
    db.session.add(teacher)

    school = School(name='школа №42')

    role_student = SystemRole.query.filter_by(name=role_student_name).first()
    user_student = SystemUser(login='st1', password='31082002', system_role=role_student, enabled=True)
    student = Student(fio='Ученик Алексей Алексеевич', system_user=user_student, birth_place='birth place',
                      birth_date='2002-08-31',
                      registration_place='reg place', actual_address='act addr', citizenship_id=1, school=school,
                      grade='1', shift=1, contact_phone=contact_phone_student, phone='89023334455')
    db.session.add(user_student)
    db.session.add(student)

    section1 = Section(name='робо', price=800)
    section2 = Section(name='веб', price=900)
    db.session.add(section1)
    db.session.add(section2)

    group = Group(name='робо-71', section=section1, teacher=teacher, start_month=8, end_month=16)
    db.session.add(group)
    db.session.add(Group(name='веб-61', section=section2, teacher=teacher, start_month=8, end_month=16))

    student_in_group = StudentInGroup(student=student, group=group, discount=100, enter_month=8, exit_month=16)
    db.session.add(student_in_group)
    db.session.add(Payment(student_in_group=student_in_group, month=1, value=800, comment=''))

    db.session.commit()


def create_schedule_times():
    for i in range(0, 20):
        db.session.add(ScheduleTime())
    db.session.commit()
