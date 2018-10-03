from flask import Blueprint, g

from app import db
from app.init_model import developer_login

api_1_0 = Blueprint('api_1_0', __name__)

from . import rests, errors


@api_1_0.after_request
def after_request(response):
    if g.current_user_app.is_authenticated and g.current_user_app.login == developer_login:
        from manage import app
        if app.config['DEVELOPER_READ_ONLY']:
            db.session.rollback()
    return response
