import datetime

from flask import g
from sqlalchemy.sql.functions import coalesce

from app.api_1_1_0.utils import get_account_type
from app.models import Group, Lesson, Attending, attending_was, AccessToken, ScheduleGroup, ScheduleTime
from app.utils import can_user_write_group


def sort_groups(query):
    from flask import g
    return query.order_by(Group.teacher_id != g.current_user_app.teacher_id_or_zero, Group.start_month.desc(),
                          Group.name)


def section_to_json(section):
    return {
        'id': section.id,
        'name': section.name,
        'price': section.price,
        'groups': [group_to_json_brief(group) for group in sort_groups(section.groups).all()]
    }


def teacher_to_json(teacher):
    return {
        'id': teacher.id,
        'fio': teacher.fio,
        'phone': teacher.phone,
        'lessonsDoneCount': teacher.lessons.filter(Lesson.date <= datetime.date.today()).count(),
        'systemUser': system_user_to_json(teacher.system_user),
        'groups': [group_to_json_brief(group) for group in sort_groups(teacher.groups).all()]
    }


def system_user_to_json(system_user):
    return {
        'id': system_user.id,
        'login': system_user.login,
        'lastSeen': system_user.last_seen.strftime("%Y-%m-%d %H:%M"),
        'lastSeenWhere': system_user.last_seen_where,
        'systemRoleName': system_user.system_role.name,
        'accountType': get_account_type(system_user),
        'enabled': system_user.enabled
    }


def developer_to_json(developer):
    return {
        'id': developer.id,
        'fio': developer.fio,
        'systemUser': system_user_to_json(developer.system_user),
    }


def master_to_json(master):
    return {
        'id': master.id,
        'fio': master.fio,
        'systemUser': system_user_to_json(master.system_user),
    }


def bot_to_json(bot):
    return {
        'id': bot.id,
        'fio': bot.fio,
        'systemUser': system_user_to_json(bot.system_user),
    }


def student_to_json_brief(student):
    return {
        'id': student.id,
        'fio': student.fio,
        'contactPhoneNumber': student.contact_phone_number,
        'contactPhoneWho': student.contact_phone_who,
        'filled': student.filled,
        'systemUser': system_user_to_json(student.system_user),
        'schoolName': student.school.name,
        'grade': student.grade,
        'shift': student.shift,
        'groups': [group_to_json_brief(group) for group in sort_groups(student.groups).all()],
        'lessonsAttendedCount': student.attendings.filter(Attending.state == attending_was).count()
    }


def student_to_json_full(student):
    return {
        'id': student.id,
        'systemUser': system_user_to_json(student.system_user),
        'filled': student.filled,
        'fio': student.fio,
        'birthDate': student.birth_date.strftime("%Y-%m-%d"),
        'birthPlace': student.birth_place,
        'registrationPlace': student.registration_place,
        'actualAddress': student.actual_address,
        'additionalInfo': student.additional_info,
        'knownFrom': student.known_from,
        'school': school_to_json(student.school),
        'grade': student.grade,
        'shift': student.shift,
        'phone': student.phone,
        'contactPhoneNumber': student.contact_phone_number,
        'contactPhoneWho': student.contact_phone_who,
        'citizenshipName': student.citizenship.name,
        'mother': parent_to_json_nullable(student.mother),
        'father': parent_to_json_nullable(student.father),
        'groups': [group_to_json_brief(group) for group in sort_groups(student.groups).all()],
        'lessonsAttendedCount': student.attendings.filter(Attending.state == attending_was).count()
    }


def school_to_json(school):
    return {
        'id': school.id,
        'name': school.name,
    }


def parent_to_json(parent):
    return {
        'id': parent.id,
        'fio': parent.fio,
        'phone': parent.phone,
        'address': parent.address,
        'email': parent.email,
        'vkLink': parent.vk_link,
        'homePhone': parent.home_phone,
        'notificationTypesString': parent.notification_types_string,
    }


def parent_to_json_nullable(parent_nullable):
    if parent_nullable is None:
        return None
    return parent_to_json(parent_nullable)


def group_to_json_brief(group):
    return {
        'id': group.id,
        'name': group.name,
        'teacherId': group.teacher.id,
        'teacherFio': group.teacher.fio,
        'startMonth': group.start_month,
        'endMonth': group.end_month,
        'sumNotConfirmed': group.sum_not_confirmed or 0 if can_user_write_group(g.current_user_app, group) else -1,
    }


def group_to_json_full(group):
    return {
        'id': group.id,
        'name': group.name,
        'teacherId': group.teacher.id,
        'teacherFio': group.teacher.fio,
        'sectionId': group.section.id,
        'sectionName': group.section.name,
        'startMonth': group.start_month,
        'endMonth': group.end_month,
        'studentsCount': group.students.count(),
        'lessonsDoneCount': group.lessons.filter(Lesson.date <= datetime.date.today()).count(),
        'sumNotConfirmed': group.sum_not_confirmed or 0 if can_user_write_group(g.current_user_app, group) else -1,
        'schedule': [schedule_group_to_json(schedule_group) for schedule_group in
                     group.schedule_groups
                         .join(ScheduleTime, ScheduleTime.id == ScheduleGroup.schedule_time_id)
                         .order_by(ScheduleGroup.day_of_week, coalesce(ScheduleTime.time, '25:59'), ScheduleTime.id)]
    }


def schedule_group_to_json(schedule_group):
    return {
        'dayOfWeek': schedule_group.day_of_week,
        'time': schedule_group.schedule_time.time
    }


def student_in_group_to_json(student_in_group):
    with_discount = can_user_write_group(g.current_user_app, student_in_group.group)
    return {
        'id': student_in_group.id,
        'systemUserEnabled': student_in_group.student.system_user.enabled,
        'studentId': student_in_group.student_id,
        'studentFio': student_in_group.student.fio,
        'groupId': student_in_group.group.id,
        'discount': student_in_group.discount if with_discount else -1,
        'enterMonth': student_in_group.enter_month,
        'exitMonth': student_in_group.exit_month,
        'lessonsAttendedCount': student_in_group.attendings_was.count(),
    }


def lesson_to_json(lesson):
    if lesson.teacher_id != lesson.group.teacher_id:
        another_teacher_fio = lesson.teacher.fio
    else:
        another_teacher_fio = None
    return {
        'id': lesson.id,
        'groupId': lesson.group_id,
        'groupName': lesson.group.name,
        'teacherId': lesson.teacher_id,
        'anotherTeacherFio': another_teacher_fio,
        'date': lesson.date.strftime("%Y-%m-%d")
    }


def attending_to_json(attending):
    return {
        'id': attending.id,
        'lessonId': attending.lesson_id,
        'studentId': attending.student_id,
        'studentFio': attending.student.fio,
        'state': attending.state,
    }


def payment_to_json(payment):
    return {
        'id': payment.id,
        'studentInGroupId': payment.student_in_group_id,
        'studentId': payment.student_in_group.student.id,
        'studentFio': payment.student_in_group.student.fio,
        'groupId': payment.student_in_group.group.id,
        'groupName': payment.student_in_group.group.name,
        'monthNumber': payment.month,
        'value': payment.value,
        'cash': payment.cash,
        'confirmed': payment.confirmed,
        'comment': payment.comment,
        'needToPay': payment.student_in_group.group.section.price - payment.student_in_group.discount
    }


def system_user_to_last_seen_info_json(system_user):
    return {
        'systemUser': system_user_to_json(system_user),
        'fio': system_user.details.fio,
        'detailsId': system_user.details.id,
    }


def system_user_access_tokens_to_json(system_user):
    access_tokens = system_user.access_tokens.order_by(AccessToken.expires.desc()).all()
    return {
        'systemUser': system_user_to_json(system_user),
        'fio': system_user.details.fio,
        'detailsId': system_user.details.id,
        'tokens': [access_token_to_json(at) for at in access_tokens],
    }


def access_token_to_json(access_token):
    return {
        'lastUse': access_token.last_use.strftime("%Y-%m-%d %H:%M"),
        'expires': access_token.expires.strftime("%Y-%m-%d %H:%M"),
        'device': access_token.device,
        'appVersion': access_token.app_version,
    }
