from app import db
from app.models import SystemRole


def create_system_roles():
    roles = [
        SystemRole(name='руководитель', details_table_name='masters'),
        SystemRole(name='преподаватель', details_table_name='teachers'),
        SystemRole(name='ученик', details_table_name='students')
    ]
    for role in roles:
        db.session.add(role)
    db.session.commit()
