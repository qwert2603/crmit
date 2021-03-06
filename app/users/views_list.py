from flask import request, render_template
from flask_login import login_required

from app.decorators import check_master_or_teacher, check_developer
from app.list_route import create_list_route
from app.models import Master, Teacher, Student, Group, Bot, Developer
from app.users import users


@users.route('/masters')
@login_required
@check_master_or_teacher
def masters_list():
    return create_list_route(
        lambda search: Master.query.filter(Master.fio.ilike('%{}%'.format(search))).order_by(Master.fio),
        'users/masters_list.html')


@users.route('/teachers')
@login_required
@check_master_or_teacher
def teachers_list():
    return create_list_route(
        lambda search: Teacher.query.filter(Teacher.fio.ilike('%{}%'.format(search))).order_by(Teacher.fio),
        'users/teachers_list.html')


@users.route('/students')
@login_required
@check_master_or_teacher
def students_list():
    group_id = request.args.get('group_id', 0, type=int)
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    if group_id > 0:
        selected_group = Group.query.get_or_404(group_id)
        pagination = selected_group.students
    else:
        selected_group = None
        pagination = Student.query
    pagination = pagination \
        .filter(Student.fio.ilike('%{}%'.format(search))) \
        .order_by(Student.filled, Student.fio) \
        .paginate(page, per_page=20, error_out=False)
    return render_template('users/students_list.html', pagination=pagination, items=pagination.items, search=search,
                           groups=Group.list_sorted_for_current_user().all(), selected_group=selected_group)


@users.route('/bots')
@login_required
@check_developer
def bots_list():
    page = request.args.get('page', 1, type=int)
    pagination = Bot.query.order_by(Bot.fio).paginate(page, per_page=20, error_out=False)
    return render_template("users/bots_list.html", pagination=pagination, items=pagination.items)


@users.route('/developers')
@login_required
@check_developer
def developers_list():
    page = request.args.get('page', 1, type=int)
    pagination = Developer.query.order_by(Developer.fio).paginate(page, per_page=20, error_out=False)
    return render_template("users/developers_list.html", pagination=pagination, items=pagination.items)
