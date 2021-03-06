from flask import Blueprint, request

from app.models import last_seen_web

users = Blueprint('users', __name__)

from . import views, views_list, views_register, views_edit, views_delete

from flask_login import current_user
from datetime import datetime
from app import db


@users.before_app_request
def before_request():
    if current_user.is_authenticated:
        if not current_user.is_developer:
            current_user.last_seen = datetime.utcnow()
            current_user.last_seen_where = last_seen_web
        for at in current_user.access_tokens_expired().all():
            db.session.delete(at)
        db.session.add(current_user._get_current_object())


@users.after_app_request
def after_request(response):
    dont_rollback_endpoints = [
        'users.login',
        'users.logout',
        'users.logout_app',
        'users.logout_app_all',
        'users.change_password',
    ]
    if request.endpoint in dont_rollback_endpoints: return response
    if current_user.is_authenticated and current_user.is_developer:
        from app_holder import app_instance
        if app_instance.config['DEVELOPER_READ_ONLY']:
            db.session.rollback()
    return response
