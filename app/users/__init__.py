from flask import Blueprint

from app.init_model import developer_login
from app.models import last_seen_web

users = Blueprint('users', __name__)

from . import views, views_list, views_register, views_edit, views_delete

from flask_login import current_user
from datetime import datetime
from app import db


@users.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        current_user.last_seen_where = last_seen_web
        for at in current_user.access_tokens_expired().all():
            db.session.delete(at)
        db.session.add(current_user)


@users.after_app_request
def after_request(response):
    if current_user.is_authenticated and current_user.login == developer_login:
        from manage import app
        if app.config['DEVELOPER_READ_ONLY']:
            db.session.rollback()
    return response
