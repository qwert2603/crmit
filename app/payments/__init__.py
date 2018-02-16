from flask import Blueprint

payments = Blueprint('payments', __name__)

from . import views
