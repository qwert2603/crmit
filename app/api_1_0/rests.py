from flask import jsonify, request

from app.api_1_0.json_utils import section_to_json, teacher_to_json
from app.api_1_0 import api_1_0
from app.models import Section, Teacher


@api_1_0.route('/sections_list')
def sections_list():
    return create_json_list(Section, Section.name, section_to_json)


@api_1_0.route('/teachers_list')
def teachers_list():
    return create_json_list(Teacher, Teacher.fio, teacher_to_json)


def create_json_list(Entity, filter_field, entity_to_json):
    list = Entity.query \
        .filter(filter_field.ilike('%{}%'.format(request.args.get('search', '', type=str)))) \
        .order_by(Entity.id) \
        .offset(request.args.get('offset', type=int)) \
        .limit(request.args.get('count', type=int)) \
        .all()
    return jsonify([entity_to_json(entity) for entity in list])
