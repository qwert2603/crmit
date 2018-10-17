from flask_login import login_required, current_user

from app.decorators import check_master
from app.init_model import developer_login, role_master_name, role_teacher_name, role_student_name
from app.main import main
from flask import render_template, jsonify, abort

from app.main.dump_utils import db_to_dump
from app.models import Group, attending_states, Master, Teacher, Student, SystemUser, SystemRole, StudentInGroup, \
    Attending
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
def check_db_integrity():
    if current_user.login != developer_login: abort(404)
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

    system_role_id_master = SystemRole.query.filter(SystemRole.name == role_master_name).first().id
    system_role_id_teacher = SystemRole.query.filter(SystemRole.name == role_teacher_name).first().id
    system_role_id_student = SystemRole.query.filter(SystemRole.name == role_student_name).first().id
    if SystemUser.query.filter(SystemUser.system_role_id == system_role_id_master).count() != Master.query.count():
        problems.append('неверное кол-во мастеров')
    if SystemUser.query.filter(SystemUser.system_role_id == system_role_id_teacher).count() != Teacher.query.count():
        problems.append('неверное кол-во учителей')
    if SystemUser.query.filter(SystemUser.system_role_id == system_role_id_student).count() != Student.query.count():
        problems.append('неверное кол-во учеников')
    if SystemUser.query.count() != Master.query.count() + Teacher.query.count() + Student.query.count():
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
    return render_template('check_db_integrity.html', problems=problems)


@main.route('/check_db_integrity/attengings_correct_group_of_students')
def check_db_integrity_attengings_correct_group_of_students():
    if current_user.login != developer_login: abort(404)
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
