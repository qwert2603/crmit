from app.decorators import check_master_or_teacher
from app.list_route import create_list_route
from app.models import Master, Teacher, Student
from app.users import users


@users.route('/masters')
@check_master_or_teacher
def masters_list():
    return create_list_route(
        lambda search: Master.query.filter(Master.fio.ilike('%{}%'.format(search))).order_by(Master.fio),
        'users/masters_list.html')


@users.route('/teachers')
@check_master_or_teacher
def teachers_list():
    return create_list_route(
        lambda search: Teacher.query.filter(Teacher.fio.ilike('%{}%'.format(search))).order_by(Teacher.fio),
        'users/teachers_list.html')


@users.route('/students')
@check_master_or_teacher
def students_list():
    return create_list_route(
        lambda search: Student.query.filter(Student.fio.ilike('%{}%'.format(search))).order_by(Student.fio),
        'users/students_list.html')
