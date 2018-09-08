from flask import jsonify, request

from app.api_1_0.json_utils import section_to_json, teacher_to_json, master_to_json, student_to_json_brief
from app.api_1_0 import api_1_0
from app.init_model import developer_login
from app.models import Section, Teacher, Master, Student, SystemUser


@api_1_0.route('/sections_list')
def sections_list():
    return create_json_list(Section, Section.name, section_to_json)


@api_1_0.route('/teachers_list')
def teachers_list():
    return create_json_list(Teacher, Teacher.fio, teacher_to_json)


@api_1_0.route('/masters_list')
def masters_list():
    return create_json_list(Master, Master.fio, master_to_json,
                            lambda query: query
                            .join(SystemUser, SystemUser.id == Master.system_user_id)
                            .filter(SystemUser.login != developer_login)
                            )


@api_1_0.route('/students_list')
def students_list():
    return create_json_list(Student, Student.fio, student_to_json_brief,
                            lambda query: query
                            .order_by(Student.filled, Student.id)
                            )


def create_json_list(Entity, filter_field, entity_to_json, more_filter=None, order_by=None):
    query_ = Entity.query \
        .filter(filter_field.ilike('%{}%'.format(request.args.get('search', '', type=str))))
    if more_filter is not None: query_ = more_filter(query_)
    if order_by is not None:
        query_ = order_by(query_)
    else:
        query_ = query_.order_by(Entity.id)
    entities_list = query_ \
        .offset(request.args.get('offset', type=int)) \
        .limit(request.args.get('count', type=int)) \
        .all()
    return jsonify([entity_to_json(entity) for entity in entities_list])
