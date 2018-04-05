from flask_login import login_required

from app.decorators import check_master_or_teacher
from app.models import Citizenship, Section, Parent, School, Group
from app.structure import structure
from app.list_route import create_list_route


@structure.route('/citizenships')
@login_required
@check_master_or_teacher
def citizenships_list():
    return create_list_route(
        lambda search: Citizenship.query.filter(Citizenship.name.ilike('%{}%'.format(search))).order_by(
            Citizenship.name),
        'structure/citizenships_list.html')


@structure.route('/groups')
@login_required
@check_master_or_teacher
def groups_list():
    return create_list_route(
        lambda search: Group.query.filter(Group.name.ilike('%{}%'.format(search))).order_by(Group.name),
        'structure/groups_list.html')


@structure.route('/parents')
@login_required
@check_master_or_teacher
def parents_list():
    return create_list_route(
        lambda search: Parent.query.filter(Parent.fio.ilike('%{}%'.format(search))).order_by(Parent.fio),
        'structure/parents_list.html')


@structure.route('/sections', methods=['GET', 'POST'])
@login_required
@check_master_or_teacher
def sections_list():
    return create_list_route(
        lambda search: Section.query.filter(Section.name.ilike('%{}%'.format(search))).order_by(Section.name),
        'structure/sections_list.html')


@structure.route('/schools')
@login_required
@check_master_or_teacher
def schools_list():
    return create_list_route(
        lambda search: School.query.filter(School.name.ilike('%{}%'.format(search))).order_by(School.name),
        'structure/schools_list.html')
