import datetime
import uuid

from flask import jsonify, request, abort, g
from sqlalchemy.sql.functions import coalesce

from app import db
from app.api_1_1_0 import api_1_1_0
from app.api_1_1_0.consts import access_token_expires_days, login_error_reason_student_account_is_not_supported, \
    login_error_reason_account_disabled, \
    login_error_reason_wrong_login_or_password
from app.api_1_1_0.decorators import access_token_required, check_master_or_teacher_access_token, \
    check_bot_access_token_with_logins, check_developer_access_token
from app.api_1_1_0.json_utils import section_to_json, teacher_to_json, master_to_json, student_to_json_brief, \
    student_to_json_full, group_to_json_full, group_to_json_brief, student_in_group_to_json, lesson_to_json, \
    attending_to_json, payment_to_json, system_user_to_last_seen_info_json, system_user_access_tokens_to_json, \
    sort_groups, developer_to_json, bot_to_json, schedule_group_to_json
from app.api_1_1_0.utils import create_json_list, create_attendings_for_all_students, token_to_hash, \
    create_payments_for_all_students, get_account_type
from app.init_model import actual_app_build_code, bot_login_dump_creator
from app.main.dump_utils import db_to_dump
from app.models import Section, Teacher, Master, Student, SystemUser, Group, Lesson, Attending, StudentInGroup, \
    attending_states, AccessToken, Payment, SystemRole, last_seen_android, last_seen_registration, Developer, Bot, \
    ScheduleGroup, ScheduleTime
from app.utils import can_user_write_group


@api_1_1_0.route('/sections_list')
@access_token_required()
@check_master_or_teacher_access_token
def sections_list():
    return create_json_list(Section, Section.name, section_to_json, order_by=lambda query: query.order_by(Section.name))


@api_1_1_0.route('/groups_list')
@access_token_required()
@check_master_or_teacher_access_token
def groups_list():
    return create_json_list(Group, Group.name, group_to_json_brief, order_by=lambda query: sort_groups(query))


@api_1_1_0.route('/teachers_list')
@access_token_required()
@check_master_or_teacher_access_token
def teachers_list():
    return create_json_list(Teacher, Teacher.fio, teacher_to_json, order_by=lambda query: query.order_by(Teacher.fio))


@api_1_1_0.route('/masters_list')
@access_token_required()
@check_master_or_teacher_access_token
def masters_list():
    return create_json_list(Master, Master.fio, master_to_json, order_by=lambda query: query.order_by(Master.fio))


@api_1_1_0.route('/bots_list')
@access_token_required()
@check_developer_access_token
def bots_list():
    return create_json_list(Bot, Bot.fio, bot_to_json, order_by=lambda query: query.order_by(Bot.fio))


@api_1_1_0.route('/developers_list')
@access_token_required()
@check_developer_access_token
def developers_list():
    return create_json_list(Developer, Developer.fio, developer_to_json,
                            order_by=lambda query: query.order_by(Developer.fio))


@api_1_1_0.route('/students_list')
@access_token_required()
@check_master_or_teacher_access_token
def students_list():
    return create_json_list(Student, Student.fio, student_to_json_brief,
                            order_by=lambda query: query.order_by(Student.filled, Student.fio))


@api_1_1_0.route('student_details/<int:student_id>')
@access_token_required()
@check_master_or_teacher_access_token
def student_details(student_id):
    return jsonify(student_to_json_full(Student.query.get_or_404(student_id)))


@api_1_1_0.route('group_details/<int:group_id>')
@access_token_required()
@check_master_or_teacher_access_token
def group_details(group_id):
    return jsonify(group_to_json_full(Group.query.get_or_404(group_id)))


@api_1_1_0.route('section_details/<int:section_id>')
@access_token_required()
@check_master_or_teacher_access_token
def section_details(section_id):
    return jsonify(section_to_json(Section.query.get_or_404(section_id)))


@api_1_1_0.route('teacher_details/<int:teacher_id>')
@access_token_required()
@check_master_or_teacher_access_token
def teacher_details(teacher_id):
    return jsonify(teacher_to_json(Teacher.query.get_or_404(teacher_id)))


@api_1_1_0.route('developer_details/<int:developer_id>')
@access_token_required()
@check_developer_access_token
def developer_details(developer_id):
    return jsonify(developer_to_json(Developer.query.get_or_404(developer_id)))


@api_1_1_0.route('bot_details/<int:bot_id>')
@access_token_required()
@check_developer_access_token
def bot_details(bot_id):
    return jsonify(bot_to_json(Bot.query.get_or_404(bot_id)))


@api_1_1_0.route('master_details/<int:master_id>')
@access_token_required()
@check_master_or_teacher_access_token
def master_details(master_id):
    return jsonify(master_to_json(Master.query.get_or_404(master_id)))


@api_1_1_0.route('students_in_group/<int:group_id>')
@access_token_required()
@check_master_or_teacher_access_token
def students_in_group(group_id):
    group = Group.query.get_or_404(group_id)
    students_in_group_list = group.students_in_group.order_by(StudentInGroup.id)
    return jsonify([student_in_group_to_json(student_in_group) for student_in_group in students_in_group_list])


@api_1_1_0.route('lessons_in_group/<int:group_id>')
@access_token_required()
@check_master_or_teacher_access_token
def lessons_in_group(group_id):
    group = Group.query.get_or_404(group_id)
    return jsonify([lesson_to_json(lesson) for lesson in group.lessons.order_by(Lesson.date)])


@api_1_1_0.route('cabinet_info', methods=['POST'])
@access_token_required()
@check_master_or_teacher_access_token
def cabinet_info():
    def get_int_param(key, default):
        if key not in request.json:
            return default
        try:
            return int(str(request.json[key]))
        except ValueError:
            return default

    g.access_token.device = str(request.json['device'])
    g.access_token.app_version = str(request.json['appVersion'])

    last_lessons_count = get_int_param('lastLessonsCount', 10)
    lessons = None
    if g.current_user_app.is_master:
        lessons = Lesson.query
    elif g.current_user_app.is_teacher:
        lessons = g.current_user_app.teacher.lessons
    else:
        abort(404)
    lessons = lessons \
        .filter(Lesson.date <= datetime.date.today()) \
        .order_by(Lesson.date.desc(), Lesson.id) \
        .limit(last_lessons_count) \
        .all()

    return jsonify(lastLessons=[lesson_to_json(lesson) for lesson in lessons],
                   actualAppBuildCode=actual_app_build_code,
                   fio=g.current_user_app.details.fio)


@api_1_1_0.route('lesson_details/<int:lesson_id>')
@access_token_required()
@check_master_or_teacher_access_token
def lesson_details(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    create_attendings_for_all_students(lesson)
    attendings = lesson.attendings \
        .join(Student, Student.id == Attending.student_id) \
        .order_by(Student.fio)
    return jsonify(group=group_to_json_brief(lesson.group),
                   teacher=teacher_to_json(lesson.teacher),
                   lesson=lesson_to_json(lesson),
                   attendings=[attending_to_json(attending) for attending in attendings])


@api_1_1_0.route('save_attending_state', methods=['POST'])
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


@api_1_1_0.route('payments/<int:group_id>')
@access_token_required()
@check_master_or_teacher_access_token
def payments_in_group(group_id):
    group = Group.query.get_or_404(group_id)
    if not can_user_write_group(g.current_user_app, group):
        abort(403)

    create_payments_for_all_students(group)

    payments = group.payments \
        .join(Student, Student.id == StudentInGroup.student_id) \
        .order_by(Student.fio)

    return jsonify(group=group_to_json_brief(group), payments=[payment_to_json(p) for p in payments])


@api_1_1_0.route('save_payment', methods=['POST'])
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

    can_confirm = g.current_user_app.is_master

    if not can_confirm and payment.confirmed:
        abort(403)

    if value < 0: value = 0
    max_value = payment.max_value
    if value > max_value: value = max_value

    if comment is None: comment = ''
    comment = comment[:32]

    payment.value = value
    payment.comment = comment
    payment.cash = is_cash

    if can_confirm: payment.confirmed = is_confirmed

    return 'ok'


@api_1_1_0.route('login', methods=['POST'])
def login():
    user_login = str(request.json['login'])
    password = str(request.json['password'])
    device = str(request.json['device'])
    app_version = str(request.json['appVersion'])

    user = SystemUser.query.filter(SystemUser.login == user_login).first()

    if user is None or not user.verify_password(password):
        return jsonify(loginErrorReason=login_error_reason_wrong_login_or_password), 400

    if not user.enabled:
        return jsonify(loginErrorReason=login_error_reason_account_disabled), 400

    if user.is_student:
        return jsonify(loginErrorReason=login_error_reason_student_account_is_not_supported), 400

    expires = datetime.datetime.utcnow() + datetime.timedelta(days=access_token_expires_days)
    token = uuid.uuid4()
    access_token = AccessToken(token_hash=token_to_hash(token), system_user_id=user.id,
                               last_use=datetime.datetime.utcnow(), expires=expires, device=device,
                               app_version=app_version)
    db.session.add(access_token)

    g.current_user_app = user

    g.current_user_app.last_seen = datetime.datetime.utcnow()
    g.current_user_app.last_seen_where = last_seen_android

    account_type = get_account_type(user)
    details_id = 0
    if user.is_developer:
        abort(400)
    elif user.is_master:
        details_id = user.master.id
    elif user.is_teacher:
        details_id = user.teacher.id
    elif user.is_bot:
        details_id = user.bot.id
    else:
        abort(400)

    return jsonify(token=token, accountType=account_type, detailsId=details_id)


@api_1_1_0.route('logout', methods=['POST'])
@access_token_required()
def logout():
    db.session.delete(g.access_token)
    return 'ok'


@api_1_1_0.route('app_info')
def app_info():
    return jsonify(actualAppBuildCode=actual_app_build_code)


@api_1_1_0.route('last_seens')
@access_token_required()
@check_developer_access_token
def last_seens():
    system_users = SystemUser.query \
        .join(SystemRole, SystemRole.id == SystemUser.system_role_id) \
        .filter(SystemUser.last_seen_where != last_seen_registration) \
        .order_by(SystemUser.last_seen.desc()) \
        .all()
    return jsonify([system_user_to_last_seen_info_json(system_user) for system_user in system_users])


@api_1_1_0.route('access_tokens')
@access_token_required()
@check_developer_access_token
def access_tokens():
    system_user_ids = [r[0] for r in db.session.query(AccessToken.system_user_id).distinct().all()]
    result_list = [system_user_access_tokens_to_json(SystemUser.query.get(suid)) for suid in system_user_ids]
    result_list = sorted(result_list, key=lambda r: r.get('tokens')[0].get('lastUse'), reverse=True)
    return jsonify(result_list)


@api_1_1_0.route('dump')
@access_token_required()
@check_bot_access_token_with_logins([bot_login_dump_creator])
def dump():
    return jsonify(db_to_dump())


@api_1_1_0.route('schedule')
@access_token_required()
@check_master_or_teacher_access_token
def schedule():
    teacher_id = request.args.get('teacherId', type=int, default=0)

    schedule_groups = ScheduleGroup.query \
        .join(ScheduleTime, ScheduleTime.id == ScheduleGroup.schedule_time_id) \
        .filter(ScheduleGroup.group_id.isnot(None)) \
        .order_by(ScheduleGroup.day_of_week, coalesce(ScheduleTime.time, '25:59'), ScheduleTime.id)

    if teacher_id != 0:
        schedule_groups = schedule_groups \
            .join(Group, Group.id == ScheduleGroup.group_id) \
            .filter(Group.teacher_id == teacher_id)

    schedule_groups = schedule_groups.all()

    return jsonify([schedule_group_to_json(g) for g in schedule_groups])
