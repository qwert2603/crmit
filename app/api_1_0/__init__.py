from flask import Blueprint, g

from app import db
from app.init_model import developer_login

api_1_0 = Blueprint('api_1_0', __name__)

from . import rests, errors


@api_1_0.before_request
def before_request():
    g.current_user_app = None


@api_1_0.after_request
def after_request(response):
    # in 'login' rest current_user_app is None
    # (because current_user_app is settled in access_token_required before request processing).
    current_user_app = g.current_user_app
    if current_user_app is not None and current_user_app.is_authenticated and current_user_app.login == developer_login:
        from manage import app
        if app.config['DEVELOPER_READ_ONLY']:
            db.session.rollback()
    return response
