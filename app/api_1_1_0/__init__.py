from flask import Blueprint, g, request

from app import db

api_1_1_0 = Blueprint('api_1_1_0', __name__)

from . import rests, errors


@api_1_1_0.before_app_request
def before_request():
    g.current_user_app = None


@api_1_1_0.after_app_request
def after_request(response):
    dont_rollback_endpoints = [
        'api_1_1_0.login',
        'api_1_1_0.logout',
    ]
    if request.endpoint in dont_rollback_endpoints: return response
    current_user_app = g.current_user_app
    if current_user_app is not None and current_user_app.is_authenticated and current_user_app.is_developer:
        from app_holder import app_instance
        if app_instance.config['DEVELOPER_READ_ONLY']:
            db.session.rollback()
    return response


@api_1_1_0.after_request
def after_request(response):
    response.headers['Content-Type'] = 'application/json; charset=utf-8'
    return response
