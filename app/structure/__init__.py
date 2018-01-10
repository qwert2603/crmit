from flask import Blueprint

structure = Blueprint('structure', __name__)

from . import views
