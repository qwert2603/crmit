from app import db
from app.models import SystemRole, SystemUser, Master, Teacher, Section, Group


def create_system_roles():
    role_master = SystemRole(name='руководитель', details_table_name='masters')
    role_teacher = SystemRole(name='преподаватель', details_table_name='teachers')
    role_student = SystemRole(name='ученик', details_table_name='students')
    roles = [role_master, role_teacher, role_student]
    for role in roles:
        db.session.add(role)

    db.session.commit()


def create_stub_models():
    create_system_roles()

    role_master = SystemRole.query.filter_by(SystemRole.name == 'руководитель').first()
    user_master = SystemUser(login='qwert2603', password='1918', system_role=role_master)
    master = Master(fio='Алекс', system_user=user_master)
    db.session.add(user_master)
    db.session.add(master)

    role_teacher = SystemRole.query.filter_by(SystemRole.name == 'преподаватель').first()
    user_teacher = SystemUser(login='te1', password='1918', system_role=role_teacher)
    teacher = Teacher(fio='учитиель №1', system_user=user_teacher)
    db.session.add(user_teacher)
    db.session.add(teacher)

    section = Section(name='робо', price=800)
    db.session.add(section)

    group = Group(name='робо-71', section=section, teacher=teacher)
    db.session.add(group)

    db.session.commit()
