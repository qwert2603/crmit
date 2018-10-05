from flask import Blueprint, g, request

from app import db
from app.init_model import developer_login

api_1_0 = Blueprint('api_1_0', __name__)

from . import rests, errors

dont_rollback_endpoints = [
    'api_1_0.login',
    'api_1_0.logout',
]


@api_1_0.before_request
def before_request():
    g.current_user_app = None


@api_1_0.after_request
def after_request(response):
    if request.endpoint in dont_rollback_endpoints: return response
    current_user_app = g.current_user_app
    if current_user_app is not None and current_user_app.is_authenticated and current_user_app.login == developer_login:
        from manage import app
        if app.config['DEVELOPER_READ_ONLY']:
            db.session.rollback()
    return response
