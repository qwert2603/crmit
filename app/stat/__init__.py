from flask import Blueprint

stat = Blueprint('stat', __name__)

from . import views
