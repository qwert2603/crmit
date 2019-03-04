from flask import request, render_template
from flask_login import login_required

from app.decorators import check_master_or_teacher, check_master
from app.list_route import create_list_route
from app.models import Citizenship, Section, Parent, School, Group, Teacher
from app.structure import structure


@structure.route('/citizenships')
@login_required
@check_master
def citizenships_list():
    return create_list_route(
        lambda search: Citizenship.query.filter(Citizenship.name.ilike('%{}%'.format(search))).order_by(
            Citizenship.name),
        'structure/citizenships_list.html')


@structure.route('/groups')
@login_required
@check_master_or_teacher
def groups_list():
    teacher_id = request.args.get('teacher_id', 0, type=int)
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    pagination = Group.list_sorted_for_current_user() \
        .filter(Group.name.ilike('%{}%'.format(search)))

    if teacher_id > 0:
        selected_teacher = Teacher.query.get_or_404(teacher_id)
        pagination = pagination.filter(Group.teacher_id == teacher_id)
    else:
        selected_teacher = None

    pagination = pagination.paginate(page, per_page=20, error_out=False)
    teachers = Teacher.query.order_by(Teacher.fio).all()
    return render_template('structure/groups_list.html', pagination=pagination, items=pagination.items,
                           selected_teacher=selected_teacher, search=search, teachers=teachers)


@structure.route('/parents')
@login_required
@check_master_or_teacher
def parents_list():
    group_id = request.args.get('group_id', 0, type=int)
    search = request.args.get('search', '')
    page = request.args.get('page', 1, type=int)
    if group_id > 0:
        selected_group = Group.query.get_or_404(group_id)
        pagination = selected_group.parents
    else:
        selected_group = None
        pagination = Parent.query
    pagination = pagination \
        .filter(Parent.fio.ilike('%{}%'.format(search))).order_by(Parent.fio) \
        .paginate(page, per_page=20, error_out=False)
    return render_template('structure/parents_list.html', pagination=pagination, items=pagination.items, search=search,
                           groups=Group.list_sorted_for_current_user().all(), selected_group=selected_group)


@structure.route('/sections', methods=['GET', 'POST'])
@login_required
@check_master_or_teacher
def sections_list():
    return create_list_route(
        lambda search: Section.query.filter(Section.name.ilike('%{}%'.format(search))).order_by(Section.name),
        'structure/sections_list.html')


@structure.route('/schools')
@login_required
@check_master
def schools_list():
    return create_list_route(
        lambda search: School.query.filter(School.name.ilike('%{}%'.format(search))).order_by(School.name),
        'structure/schools_list.html')
