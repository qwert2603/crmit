from app.models import Group


def section_to_json(section):
    return {
        'id': section.id,
        'name': section.name,
        'price': section.price,
        'groups': [{
            'id': group.id,
            'name': group.name,
            'teacherFio': group.teacher.fio
        } for group in section.groups.order_by(Group.id).all()]
    }


def teacher_to_json(teacher):
    return {
        'id': teacher.id,
        'fio': teacher.fio,
        'phone': teacher.phone,
        'lessonsCount': teacher.lessons.count(),
        'systemUser': system_user_to_json(teacher.system_user),
        'groups': [{
            'id': group.id,
            'name': group.name,
        } for group in teacher.groups.order_by(Group.id).all()]
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
        'groups': [{
            'id': group.id,
            'name': group.name,
        } for group in student.groups.order_by(Group.id).all()]
    }


def student_to_json_full(student):
    return {
        'id': student.id,
        'systemUser': system_user_to_json(student.system_user),
        'fio': student.fio,
        'birthDate': student.birth_date.strftime("%d.%m.%Y"),
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
        'parents': [parent_to_json(parent) for parent in student.parents],
        'groups': [{
            'id': group.id,
            'name': group.name,
            'teacherFio': group.teacher.fio
        } for group in student.groups.order_by(Group.id).all()]
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
        'notification_types_string': parent.notification_types_string,
    }