from flask import Blueprint

lessons = Blueprint('lessons', __name__)

from . import views
