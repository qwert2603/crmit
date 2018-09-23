import datetime

from app.models import Group, Lesson, Attending, attending_was


def section_to_json(section):
    return {
        'id': section.id,
        'name': section.name,
        'price': section.price,
        'groups': [group_to_json_brief(group) for group in section.groups.order_by(Group.id).all()]
    }


def teacher_to_json(teacher):
    return {
        'id': teacher.id,
        'fio': teacher.fio,
        'phone': teacher.phone,
        'lessonsDoneCount': teacher.lessons.filter(Lesson.date <= datetime.date.today()).count(),
        'systemUser': system_user_to_json(teacher.system_user),
        'groups': [group_to_json_brief(group) for group in teacher.groups.order_by(Group.id).all()]
    }


def system_user_to_json(system_user):
    return {
        'id': system_user.id,
        'login': system_user.login,
        'lastSeen': system_user.last_seen.timestamp() * 1000000,
        'systemRoleName': system_user.system_role.name,
        'enabled': system_user.enabled
    }


def master_to_json(master):
    return {
        'id': master.id,
        'fio': master.fio,
        'systemUser': system_user_to_json(master.system_user),
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
        'groups': [group_to_json_brief(group) for group in student.groups.order_by(Group.id).all()],
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
        'groups': [group_to_json_brief(group) for group in student.groups.order_by(Group.id).all()],
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
    }


def student_in_group_to_json(student_in_group):
    return {
        'id': student_in_group.id,
        'systemUserEnabled': student_in_group.student.system_user.enabled,
        'studentId': student_in_group.student_id,
        'studentFio': student_in_group.student.fio,
        'groupId': student_in_group.group.id,
        'discount': student_in_group.discount,
        'enterMonth': student_in_group.enter_month,
        'exitMonth': student_in_group.exit_month,
        'lessonsAttendedCount': student_in_group.attendings_was.count(),
    }


def lesson_to_json(lesson):
    return {
        'id': lesson.id,
        'groupId': lesson.group.id,
        'date': lesson.date.strftime("%Y-%m-%d")
    }


def attending_to_json(attending):
    return {
        'id': attending.id,
        'lessonId': attending.lesson_id,
        'studentId': attending.student_id,
        'state': attending.state,
    }
