from flask import Blueprint

auth = Blueprint('auth', __name__)

from . import views
from flask_login import current_user
from datetime import datetime
from app import db


@auth.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.add(current_user)
