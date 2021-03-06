from flask import redirect, url_for, flash, abort
from flask_login import login_required

from app import db
from app.decorators import check_master, check_master_or_teacher
from app.is_removable_check import is_citizenship_removable, is_parent_removable, is_school_removable, \
    is_section_removable, is_group_removable
from app.models import Citizenship, Section, Parent, School, Group
from app.structure import structure
from app.utils import redirect_back_or_home


@structure.route('/delete_citizenship/<int:id>')
@login_required
@check_master
def delete_citizenship(id):
    citizenship = Citizenship.query.get_or_404(id)
    if not is_citizenship_removable(citizenship): abort(409)
    db.session.delete(citizenship)
    flash('гражданство {} удалено'.format(citizenship.name))
    return redirect_back_or_home()


@structure.route('/delete_section/<int:id>')
@login_required
@check_master
def delete_section(id):
    section = Section.query.get_or_404(id)
    if not is_section_removable(section): abort(409)
    db.session.delete(section)
    flash('секция {} удалена'.format(section.name))
    return redirect_back_or_home()


@structure.route('/delete_school/<int:id>')
@login_required
@check_master
def delete_school(id):
    school = School.query.get_or_404(id)
    if not is_school_removable(school): abort(409)
    db.session.delete(school)
    flash('школа {} удалена'.format(school.name))
    return redirect_back_or_home()


@structure.route('/delete_parent/<int:id>')
@login_required
@check_master_or_teacher
def delete_parent(id):
    parent = Parent.query.get_or_404(id)
    if not is_parent_removable(parent): abort(409)
    db.session.delete(parent)
    flash('родитель {} удален'.format(parent.fio))
    return redirect_back_or_home()


@structure.route('/delete_group/<int:id>')
@login_required
@check_master
def delete_group(id):
    group = Group.query.get_or_404(id)
    if not is_group_removable(group): abort(409)
    group.notifications.delete()
    db.session.delete(group)
    flash('группа {} удалена'.format(group.name))
    return redirect_back_or_home()
