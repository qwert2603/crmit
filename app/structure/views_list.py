from flask import render_template, request

from app.decorators import check_master_or_teacher
from app.models import Citizenship, Section, Parent, School, Group
from app.structure import structure


# todo: search

@structure.route('/citizenships')
@check_master_or_teacher
def citizenships_list():
    page = request.args.get('page', 1, type=int)
    pagination = Citizenship.query.order_by(Citizenship.name).paginate(page, per_page=10, error_out=False)
    return render_template('structure/citizenships_list.html', pagination=pagination, citizenships=pagination.items)


@structure.route('/groups')
@check_master_or_teacher
def groups_list():
    page = request.args.get('page', 1, type=int)
    pagination = Group.query.order_by(Group.name).paginate(page, per_page=10, error_out=False)
    return render_template('structure/groups_list.html', pagination=pagination, groups=pagination.items)


@structure.route('/parents')
@check_master_or_teacher
def parents_list():
    page = request.args.get('page', 1, type=int)
    pagination = Parent.query.order_by(Parent.fio).paginate(page, per_page=10, error_out=False)
    return render_template('structure/parents_list.html', pagination=pagination, parents=pagination.items)


@structure.route('/sections')
@check_master_or_teacher
def sections_list():
    page = request.args.get('page', 1, type=int)
    pagination = Section.query.order_by(Section.name).paginate(page, per_page=10, error_out=False)
    return render_template('structure/sections_list.html', pagination=pagination, sections=pagination.items)


@structure.route('/schools')
@check_master_or_teacher
def schools_list():
    page = request.args.get('page', 1, type=int)
    pagination = School.query.order_by(School.name).paginate(page, per_page=10, error_out=False)
    return render_template('structure/schools_list.html', pagination=pagination, schools=pagination.items)
