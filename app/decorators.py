from functools import wraps
from flask import abort
from flask_login import current_user
from app.init_model import role_master_name, role_teacher_name
from app.models import Group


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


def check_access_group_write():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated: abort(403)
            if current_user.system_role.name == role_master_name: return f(*args, **kwargs)
            if current_user.system_role.name == role_teacher_name:
                group = Group.query.get_or_404(kwargs['group_id'])
                if current_user.teacher.id == group.teacher_id:
                    return f(*args, **kwargs)
            abort(403)

        return decorated_function

    return decorator
