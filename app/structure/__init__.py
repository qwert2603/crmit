from flask import Blueprint

structure = Blueprint('structure', __name__)

from . import views_add, views_edit, views_list, views_delete, views
