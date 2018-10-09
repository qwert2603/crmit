import datetime
import uuid

from flask import jsonify, request, abort, g

from app import db
from app.api_1_0_1 import api_1_0_1
from app.api_1_0_1.consts import access_token_expires_days, account_type_master, \
    account_type_teacher, login_error_reason_student_account_is_not_supported, login_error_reason_account_disabled, \
    login_error_reason_wrong_login_or_password
from app.api_1_0_1.decorators import access_token_required, check_master_or_teacher_access_token
from app.api_1_0_1.json_utils import section_to_json, teacher_to_json, master_to_json, student_to_json_brief, \
    student_to_json_full, group_to_json_full, group_to_json_brief, student_in_group_to_json, lesson_to_json, \
    attending_to_json, payment_to_json
from app.api_1_0_1.utils import create_json_list, create_attendings_for_all_students, token_to_hash, \
    create_payments_for_all_students
from app.init_model import developer_login, role_student_name, role_master_name, role_teacher_name
from app.models import Section, Teacher, Master, Student, SystemUser, Group, Lesson, Attending, StudentInGroup, \
    attending_states, AccessToken, Payment
from app.utils import can_user_write_group


@api_1_0_1.route('/sections_list')
@access_token_required()
@check_master_or_teacher_access_token
def sections_list():
    return create_json_list(Section, Section.name, section_to_json)


@api_1_0_1.route('/groups_list')
@access_token_required()
@check_master_or_teacher_access_token
def groups_list():
    return create_json_list(Group, Group.name, group_to_json_brief)


@api_1_0_1.route('/teachers_list')
@access_token_required()
@check_master_or_teacher_access_token
def teachers_list():
    return create_json_list(Teacher, Teacher.fio, teacher_to_json)


@api_1_0_1.route('/masters_list')
@access_token_required()
@check_master_or_teacher_access_token
def masters_list():
    return create_json_list(Master, Master.fio, master_to_json,
                            lambda query: query
                            .join(SystemUser, SystemUser.id == Master.system_user_id)
                            .filter(SystemUser.login != developer_login)
                            )


@api_1_0_1.route('/students_list')
@access_token_required()
@check_master_or_teacher_access_token
def students_list():
    return create_json_list(Student, Student.fio, student_to_json_brief,
                            lambda query: query
                            .order_by(Student.filled, Student.id)
                            )


@api_1_0_1.route('student_details/<int:student_id>')
@access_token_required()
@check_master_or_teacher_access_token
def student_details(student_id):
    return jsonify(student_to_json_full(Student.query.get_or_404(student_id)))


@api_1_0_1.route('group_details/<int:group_id>')
@access_token_required()
@check_master_or_teacher_access_token
def group_details(group_id):
    return jsonify(group_to_json_full(Group.query.get_or_404(group_id)))


@api_1_0_1.route('section_details/<int:section_id>')
@access_token_required()
@check_master_or_teacher_access_token
def section_details(section_id):
    return jsonify(section_to_json(Section.query.get_or_404(section_id)))


@api_1_0_1.route('teacher_details/<int:teacher_id>')
@access_token_required()
@check_master_or_teacher_access_token
def teacher_details(teacher_id):
    return jsonify(teacher_to_json(Teacher.query.get_or_404(teacher_id)))


@api_1_0_1.route('master_details/<int:master_id>')
@access_token_required()
@check_master_or_teacher_access_token
def master_details(master_id):
    master = Master.query.get_or_404(master_id)
    if master.system_user.login == developer_login and g.current_user_app.login != developer_login:
        abort(404)
    return jsonify(master_to_json(master))


@api_1_0_1.route('students_in_group/<int:group_id>')
@access_token_required()
@check_master_or_teacher_access_token
def students_in_group(group_id):
    group = Group.query.get_or_404(group_id)
    students_in_group_list = group.students_in_group.order_by(StudentInGroup.id)
    return jsonify([student_in_group_to_json(student_in_group) for student_in_group in students_in_group_list])


@api_1_0_1.route('lessons_in_group/<int:group_id>')
@access_token_required()
@check_master_or_teacher_access_token
def lessons_in_group(group_id):
    group = Group.query.get_or_404(group_id)
    return jsonify([lesson_to_json(lesson) for lesson in group.lessons.order_by(Lesson.date)])


@api_1_0_1.route('attendings_of_lesson/<int:lesson_id>')
@access_token_required()
@check_master_or_teacher_access_token
def attendings_of_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    create_attendings_for_all_students(lesson)
    attendings = lesson.attendings \
        .join(Student, Student.id == Attending.student_id) \
        .order_by(Student.fio)
    return jsonify([attending_to_json(attending) for attending in attendings])


@api_1_0_1.route('save_attending_state', methods=['POST'])
@access_token_required()
@check_master_or_teacher_access_token
def save_attending_state():
    def int_or_400(key):
        if key not in request.json:
            abort(400)
        try:
            return int(str(request.json[key]))
        except ValueError:
            abort(400)

    attending_id = int_or_400('attendingId')
    attending_state = int_or_400('attendingState')
    if attending_state not in attending_states:
        abort(400)

    attending = Attending.query.get_or_404(attending_id)

    if not can_user_write_group(g.current_user_app, attending.lesson.group):
        abort(403)

    attending.state = attending_state
    return 'ok'


@api_1_0_1.route('payments/<int:group_id>/<int:month_number>')
@access_token_required()
@check_master_or_teacher_access_token
def payments_in_month(group_id, month_number):
    group = Group.query.get_or_404(group_id)
    if not can_user_write_group(g.current_user_app, group):
        abort(403)
    if month_number < group.start_month or month_number > group.end_month:
        abort(404)

    create_payments_for_all_students(group, month_number)

    payments = group.payments_in_month(month_number) \
        .join(Student, Student.id == StudentInGroup.student_id) \
        .order_by(Student.fio)

    return jsonify([payment_to_json(p) for p in payments])


@api_1_0_1.route('save_payment', methods=['POST'])
@access_token_required()
@check_master_or_teacher_access_token
def save_payment():
    def int_or_400(key):
        if key not in request.json:
            abort(400)
        try:
            return int(str(request.json[key]))
        except ValueError:
            abort(400)

    payment_id = int_or_400('paymentId')
    value = int_or_400('value')
    comment = request.json.get('comment')
    is_cash = str(request.json.get('cash')) == 'True'
    is_confirmed = str(request.json.get('confirmed')) == 'True'

    payment = Payment.query.get_or_404(payment_id)

    if not can_user_write_group(g.current_user_app, payment.student_in_group.group):
        abort(403)

    if value < 0: value = 0
    max_value = payment.max_value
    if value > max_value: value = max_value

    if comment is None: comment = ''
    comment = comment[:32]

    payment.value = value
    payment.comment = comment
    payment.cash = is_cash
    can_confirm = g.current_user_app.system_role.name == role_master_name
    if can_confirm: payment.confirmed = is_confirmed

    return 'ok'


@api_1_0_1.route('login', methods=['POST'])
def login():
    user_login = str(request.json['login'])
    password = str(request.json['password'])

    user = SystemUser.query.filter(SystemUser.login == user_login).first()

    if user is None or not user.verify_password(password):
        return jsonify(loginErrorReason=login_error_reason_wrong_login_or_password), 400

    if not user.enabled:
        return jsonify(loginErrorReason=login_error_reason_account_disabled), 400

    if user.system_role.name == role_student_name:
        return jsonify(loginErrorReason=login_error_reason_student_account_is_not_supported), 400

    expires = datetime.datetime.utcnow() + datetime.timedelta(days=access_token_expires_days)
    token = uuid.uuid4()
    access_token = AccessToken(token_hash=token_to_hash(token), system_user_id=user.id, expires=expires)
    db.session.add(access_token)

    account_type = 0
    details_id = 0
    if user.system_role.name == role_master_name:
        account_type = account_type_master
        details_id = user.master.id
    if user.system_role.name == role_teacher_name:
        account_type = account_type_teacher
        details_id = user.teacher.id

    return jsonify(token=token, accountType=account_type, detailsId=details_id)


@api_1_0_1.route('logout', methods=['POST'])
@access_token_required()
def logout():
    db.session.delete(g.access_token)
    return 'ok'