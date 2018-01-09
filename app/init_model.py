from app import db
from app.models import SystemRole, SystemUser, Master


def create_system_roles():
    role_master = SystemRole(name='руководитель', details_table_name='masters')
    roles = [
        role_master,
        SystemRole(name='преподаватель', details_table_name='teachers'),
        SystemRole(name='ученик', details_table_name='students')
    ]
    for role in roles:
        db.session.add(role)
    system_user = SystemUser(login='qwert2603', password='1918', system_role=role_master)
    master = Master(fio='Алекс', system_user=system_user)
    db.session.add(system_user)
    db.session.add(master)
    db.session.commit()
