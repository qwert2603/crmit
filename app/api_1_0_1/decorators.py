from functools import wraps

import datetime
from flask import request, abort, g

from app import db
from app.api_1_0_1.utils import token_to_hash
from app.init_model import role_master_name, role_teacher_name, developer_login
from app.models import AccessToken, last_seen_android


def access_token_required():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.args.get('access_token')
            if token is None:
                abort(401)
            access_token = AccessToken.query.filter(AccessToken.token_hash == token_to_hash(token)).first()
            if access_token is None:
                abort(401)
            if access_token.expires < datetime.datetime.utcnow():
                db.session.delete(access_token)
                abort(401)
            if not access_token.system_user.enabled:
                db.session.delete(access_token)
                abort(401)
            from app.api_1_0_1.rests import access_token_expires_days
            access_token.expires = datetime.datetime.utcnow() + datetime.timedelta(days=access_token_expires_days)
            g.access_token = access_token
            g.current_user_app = access_token.system_user

            if g.current_user_app.login != developer_login:
                g.current_user_app.last_seen = datetime.datetime.utcnow()
                g.current_user_app.last_seen_where = last_seen_android
            for at in g.current_user_app.access_tokens_expired().all():
                db.session.delete(at)

            return f(*args, **kwargs)

        return decorated_function

    return decorator


def check_system_role_access_token(system_role_names):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if g.current_user_app is None or g.current_user_app.system_role.name not in system_role_names:
                abort(403)
            return f(*args, **kwargs)

        return decorated_function

    return decorator


def check_master_access_token(f):
    return check_system_role_access_token([role_master_name])(f)


def check_teacher_access_token(f):
    return check_system_role_access_token([role_teacher_name])(f)


def check_master_or_teacher_access_token(f):
    return check_system_role_access_token([role_master_name, role_teacher_name])(f)


def check_developer_access_token():
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if g.current_user_app.login != developer_login:
                abort(404)
            return f(*args, **kwargs)

        return decorated_function

    return decorator
