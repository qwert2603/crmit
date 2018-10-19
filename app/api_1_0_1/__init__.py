from flask import Blueprint, g, request

from app import db
from app.init_model import developer_login

api_1_0_1 = Blueprint('api_1_0_1', __name__)

from . import rests, errors


@api_1_0_1.before_request
def before_request():
    g.current_user_app = None


@api_1_0_1.after_request
def after_request(response):
    dont_rollback_endpoints = [
        'api_1_0_1.login',
        'api_1_0_1.logout',
    ]
    if request.endpoint in dont_rollback_endpoints: return response
    current_user_app = g.current_user_app
    if current_user_app is not None and current_user_app.is_authenticated and current_user_app.login == developer_login:
        from app_holder import app_instance
        if app_instance.config['DEVELOPER_READ_ONLY']:
            db.session.rollback()
    return response
