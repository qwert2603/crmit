from flask import Blueprint

notifications = Blueprint('notifications', __name__)

from . import views
