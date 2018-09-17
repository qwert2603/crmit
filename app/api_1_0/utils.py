from flask import request, jsonify

from app import db
from app.models import Attending, attending_was_not
from app.utils import number_of_month_for_date


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


def create_attendings_for_all_students(lesson):
    attending_exist_student_ids = [a.student_id for a in lesson.attendings]

    for student in lesson.group.students_in_month(number_of_month_for_date(lesson.date)):
        if student.id not in attending_exist_student_ids:
            db.session.add(Attending(lesson_id=lesson.id, student_id=student.id, state=attending_was_not))
    db.session.commit()
