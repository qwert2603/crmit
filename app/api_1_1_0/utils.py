from flask import request, jsonify

from app import db
from app.api_1_1_0.consts import account_type_developer, account_type_master, account_type_teacher, account_type_bot, \
    account_type_student
from app.models import Attending, attending_was_not, Payment
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


def create_payments_for_all_students(group):
    for month_number in range(group.start_month, group.end_month + 1):
        payment_exist_student_in_group_ids = [p.student_in_group_id for p in group.payments_in_month(month_number)]

        for student_in_group in group.students_in_group_in_month(month_number):
            if student_in_group.id not in payment_exist_student_in_group_ids:
                db.session.add(Payment(student_in_group=student_in_group, month=month_number, value=0, cash=True,
                                       confirmed=False, comment=""))
    db.session.commit()


def token_to_hash(token):
    import hashlib, binascii
    from app_holder import app_instance

    dk = hashlib.pbkdf2_hmac('sha256', str(token).encode('utf-8'), app_instance.config['ACCESS_TOKEN_SALT'], 100000)
    return str(binascii.hexlify(dk))


def get_account_type(system_user):
    if system_user.is_developer:
        return account_type_developer
    elif system_user.is_master:
        return account_type_master
    elif system_user.is_teacher:
        return account_type_teacher
    elif system_user.is_bot:
        return account_type_bot
    elif system_user.is_student:
        return account_type_student
