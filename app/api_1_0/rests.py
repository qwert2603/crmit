from flask import jsonify

from app.api_1_0.json_utils import section_to_json, teacher_to_json
from app.api_1_0 import api_1_0
from app.models import Section, Teacher


@api_1_0.route('/sections_list')
def sections_list():
    return jsonify([section_to_json(section) for section in Section.query.order_by(Section.id).all()])


@api_1_0.route('/teachers_list')
def teachers_list():
    return jsonify([teacher_to_json(teacher) for teacher in Teacher.query.order_by(Teacher.id).all()])
