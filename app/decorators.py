from functools import wraps

from flask import abort, request
from flask_login import current_user

from app.init_model import role_master_name, role_teacher_name, role_student_name
from app.models import Group
from app.utils import can_user_write_group


def check_system_role(system_role_names):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated or current_user.system_role.name not in system_role_names:
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def check_master(f):
    return check_system_role([role_master_name])(f)


def check_teacher(f):
    return check_system_role([role_teacher_name])(f)


def check_master_or_teacher(f):
    return check_system_role([role_master_name, role_teacher_name])(f)


def check_student(f):
    return check_system_role([role_student_name])(f)

def check_access_group_write():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            group_id = kwargs.get('group_id') or request.args.get('group_id', 0, type=int)
            if not can_user_write_group(current_user, Group.query.get_or_404(group_id)):
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator
