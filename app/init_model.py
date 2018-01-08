from app import db
from app.models import SystemRole, SystemUser


def create_system_roles():
    role_master = SystemRole(name='руководитель', details_table_name='masters')
    roles = [
        role_master,
        SystemRole(name='преподаватель', details_table_name='teachers'),
        SystemRole(name='ученик', details_table_name='students')
    ]
    for role in roles:
        db.session.add(role)
    db.session.add(SystemUser(login='qwert2603', password='1918', system_role=role_master))
    db.session.commit()
