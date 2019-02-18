from flask_login import login_required

from app.decorators import check_student
from app.student import student

@student.route('/my_info')
@login_required
@check_student
def my_info():
    return '42'
