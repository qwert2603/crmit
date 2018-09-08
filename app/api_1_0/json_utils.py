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
        'groups': [{
            'id': group.id,
            'name': group.name,
        } for group in student.groups.order_by(Group.id).all()]
    }


def student_to_json_full(student):
    return {
        'id': student.id,
        'fio': student.fio,
        # todo
    }
