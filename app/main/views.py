import datetime
import os

from flask import render_template, jsonify, request
from flask_login import login_required

from app.decorators import check_master, check_developer
from app.init_model import role_master_name, role_teacher_name, role_student_name, role_bot_name, role_developer_name
from app.main import main
from app.main.dump_utils import db_to_dump
from app.models import Group, attending_states, Master, Teacher, Student, SystemUser, SystemRole, StudentInGroup, \
    Attending, Bot, Developer, PageVisit, Notification, receiver_type_student_in_group, receiver_type_group, Message, \
    MessageDetails, Parent, notification_types_list
from app.utils import start_date_of_month, end_date_of_month, get_month_name


@main.route('/')
def index():
    return render_template('index.html', hide_who_u_r=True)


@main.route('/anth')
@login_required
@check_master
def anth():
    return render_template('anth.html')


@main.route('/dump')
@login_required
@check_master
def dump():
    return jsonify(db_to_dump())


@main.route('/check_db_integrity')
@login_required
@check_developer
def check_db_integrity():
    problems = list()

    for master in Master.query.all():
        if master.system_user.system_role.name != role_master_name:
            problems.append('у мастера id={} ({}) неверная системная роль'.format(master.id, master.fio))
    for teacher in Teacher.query.all():
        if teacher.system_user.system_role.name != role_teacher_name:
            problems.append('у учителя id={} ({}) неверная системная роль'.format(teacher.id, teacher.fio))
    for student in Student.query.all():
        if student.system_user.system_role.name != role_student_name:
            problems.append('у ученика id={} ({}) неверная системная роль'.format(student.id, student.fio))
    for bot in Bot.query.all():
        if bot.system_user.system_role.name != role_bot_name:
            problems.append('у бота id={} ({}) неверная системная роль'.format(bot.id, bot.fio))
    for developer in Developer.query.all():
        if developer.system_user.system_role.name != role_developer_name:
            problems.append('у разработчика id={} ({}) неверная системная роль'.format(developer.id, developer.fio))

    system_role_id_master = SystemRole.query.filter(SystemRole.name == role_master_name).first().id
    system_role_id_teacher = SystemRole.query.filter(SystemRole.name == role_teacher_name).first().id
    system_role_id_student = SystemRole.query.filter(SystemRole.name == role_student_name).first().id
    system_role_id_bot = SystemRole.query.filter(SystemRole.name == role_bot_name).first().id
    system_role_id_developer = SystemRole.query.filter(SystemRole.name == role_developer_name).first().id

    if SystemUser.query.filter(SystemUser.system_role_id == system_role_id_master).count() != Master.query.count():
        problems.append('неверное кол-во мастеров')
    if SystemUser.query.filter(SystemUser.system_role_id == system_role_id_teacher).count() != Teacher.query.count():
        problems.append('неверное кол-во учителей')
    if SystemUser.query.filter(SystemUser.system_role_id == system_role_id_student).count() != Student.query.count():
        problems.append('неверное кол-во учеников')
    if SystemUser.query.filter(SystemUser.system_role_id == system_role_id_bot).count() != Bot.query.count():
        problems.append('неверное кол-во ботов')
    if SystemUser.query \
            .filter(SystemUser.system_role_id == system_role_id_developer).count() != Developer.query.count():
        problems.append('неверное кол-во разработчиков')

    if SystemUser.query.count() != Master.query.count() + Teacher.query.count() + Student.query.count() \
            + Bot.query.count() + Developer.query.count():
        problems.append('кол-во системных пользователей не равно кол-ву пользователей')

    for group in Group.query.all():
        if group.start_month > group.end_month:
            problems.append('группа id={} ({}) - конец раньше начала'.format(group.id, group.name))
        if group.end_month - group.start_month >= 12:
            problems.append('группа id={} ({}) функционирует больше 12 месяцев'.format(group.id, group.name))
        start_date = start_date_of_month(group.start_month)
        end_date = end_date_of_month(group.end_month)
        for lesson in group.lessons.all():
            if lesson.date < start_date or lesson.date > end_date:
                problems.append('занятие id={} ({} / {}) выходит за рамки функционирования группы'
                                .format(lesson.id, group.name, lesson.date))
            for attending in lesson.attendings.all():
                if attending.state not in attending_states:
                    problems.append('неизвестный статус посещения id={} ({} / {} / {})'
                                    .format(attending.id, attending.student.fio, attending.lesson.date, group.name))
        for student_in_group in group.students_in_group.all():
            if student_in_group.enter_month < group.start_month or student_in_group.exit_month > group.end_month \
                    or student_in_group.enter_month > student_in_group.exit_month:
                problems.append('ученик в группе id={} ({} / {}) выходит за рамки функционирования группы'
                                .format(student_in_group.id, student_in_group.student.fio, group.name))
            for payment in student_in_group.payments.all():
                if payment.month < student_in_group.enter_month or payment.month > student_in_group.exit_month:
                    problems.append('платеж id={} ({} / {} / {}) выходит за рамки нахождения ученика в группе'
                                    .format(payment.id, group.name, student_in_group.student.fio,
                                            get_month_name(payment.month)))
                if payment.value < 0 or payment.value > payment.max_value:
                    problems.append('неверная сумма платежа id={} ({} / {} / {})'
                                    .format(payment.id, group.name, student_in_group.student.fio,
                                            get_month_name(payment.month)))
    notification_types_overflow = 1
    for i in range(0, len(notification_types_list)):
        notification_types_overflow <<= 1
    for parent in Parent.query.all():
        if parent.notification_types < 0 or parent.notification_types >= notification_types_overflow:
            problems.append('у родителя id={} неверные типы уведомлений'.format(parent.id))

    return render_template('check_db_integrity.html', problems=problems)


@main.route('/check_db_integrity/attengings_correct_group_of_students')
@login_required
@check_developer
def check_db_integrity_attengings_correct_group_of_students():
    problems = list()

    students_group_map = dict()
    for student_in_group in StudentInGroup.query.all():
        group_ids = students_group_map.get(student_in_group.student_id)
        if group_ids is None:
            group_ids = set()
            students_group_map[student_in_group.student_id] = group_ids
        group_ids.add(student_in_group.group_id)

    for attending in Attending.query.all():
        if attending.lesson.group_id not in students_group_map[attending.student_id]:
            problems.append(
                'ученик посетил занятие группы, в которой не состоит; attending_id={} ({} / {} / {})'
                    .format(attending.id, attending.student.fio, attending.lesson.date, attending.lesson.group.name))

    return render_template('check_db_integrity__attengings_correct_group_of_students.html', problems=problems)


@main.route('/check_db_integrity/notifications_and_messages')
@login_required
@check_developer
def check_db_integrity_notifications_and_messages():
    problems = list()

    users_id_by_role_id = dict()

    for system_user in SystemUser.query.all():
        users_ids = users_id_by_role_id.get(system_user.system_role.id)
        if users_ids is None:
            users_ids = set()
            users_id_by_role_id[system_user.system_role.id] = users_ids
        users_ids.add(system_user.id)

    masters = users_id_by_role_id.get(SystemRole.query.filter(SystemRole.name == role_master_name).first().id) or set()
    teachers = users_id_by_role_id.get(
        SystemRole.query.filter(SystemRole.name == role_teacher_name).first().id) or set()
    students = users_id_by_role_id.get(
        SystemRole.query.filter(SystemRole.name == role_student_name).first().id) or set()
    bots = users_id_by_role_id.get(SystemRole.query.filter(SystemRole.name == role_bot_name).first().id) or set()
    developers = users_id_by_role_id.get(
        SystemRole.query.filter(SystemRole.name == role_developer_name).first().id) or set()

    groups_ids = set()
    students_in_groups_ids = set()

    for group in Group.query.all(): groups_ids.add(group.id)
    for sig in StudentInGroup.query.all(): students_in_groups_ids.add(sig.id)

    for notification in Notification.query.all():
        if notification.sender_id not in masters and notification.sender_id not in teachers:
            problems.append('неверная роль у отправителя уведомления id={}'.format(notification.id))
        if notification.receiver_type == receiver_type_group:
            if notification.receiver_id not in groups_ids:
                problems.append('уведомление id={} отправлено несуществующей группе'.format(notification.id))
        elif notification.receiver_type == receiver_type_student_in_group:
            if notification.receiver_id not in students_in_groups_ids:
                problems.append('увед-е id={} отправлено несуществующему студенту в группе'.format(notification.id))
        else:
            problems.append('неверный receiver_type у уведомления id={}'.format(notification.id))

    if Message.query.count() != 2 * MessageDetails.query.count():
        problems.append('неверное кол-во сообщений / деталей сообщений')

    for message in Message.query.all():
        if message.owner_id == message.receiver_id:
            problems.append('сообщение id={} отправлено самому себе'.format(message.id))
        if message.owner_id in students and message.receiver_id in students:
            problems.append('сообщение id={} отправлено между учениками'.format(message.id))
        if message.owner_id in bots or message.receiver_id in bots \
                or message.owner_id in developers or message.receiver_id in developers:
            problems.append('сообщение id={} ссылается на бота или разработчика'.format(message.id))

    messages_by_details_id = dict()

    for message in Message.query.all():
        details_id = message.message_details_id
        messages_of_details_id = messages_by_details_id.get(details_id)
        if messages_of_details_id is None:
            messages_of_details_id = list()
            messages_by_details_id[details_id] = messages_of_details_id
        messages_of_details_id.append(message)

    for md in MessageDetails.query.all():
        messages_of_details_id = messages_by_details_id.get(md.id)
        if messages_of_details_id is None or len(messages_of_details_id) != 2:
            problems.append('на детали о сообщений id={} ссылается неверное кол-во сообщений'.format(md.id))
        else:
            if messages_of_details_id[0].forward == messages_of_details_id[1].forward:
                problems.append('на детали о сообщений id={} ссылаются сообщения в одном направлении'.format(md.id))
            if messages_of_details_id[0].owner_id != messages_of_details_id[1].receiver_id \
                    or messages_of_details_id[0].receiver_id != messages_of_details_id[1].owner_id:
                problems.append('на детали о сообщений id={} ссылаются сообщения между разными юзерами'.format(md.id))

    return render_template('check_db_integrity__notifications_and_messages.html', problems=problems)


@main.route('/visit_stats')
@login_required
@check_developer
def visit_stats():
    pages = PageVisit.query.order_by(PageVisit.visits_count.desc(), PageVisit.page_name).all()
    return render_template("visit_stats.html", pages=pages)


@main.route('/upload_logs', methods=['POST'])
def upload_logs():
    try:
        now_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        dir = 'logs'
        os.makedirs(dir, exist_ok=True)
        device_uuid = request.json.get("deviceUuid")
        filename = '{}/{}_{}.txt'.format(dir, device_uuid, now_string)
        import codecs
        write_file = codecs.open(filename, 'w', "utf-8")
        write_file.write(request.json.get("logs"))
        write_file.close()
        return 'ok'
    except Exception as e:
        return str(e), 404
