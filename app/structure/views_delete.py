from flask import redirect, url_for, flash
from flask_login import login_required

from app import db
from app.decorators import check_master
from app.models import Citizenship, Section, Parent, School, Group
from app.structure import structure


@structure.route('/delete_citizenship/<int:id>')
@login_required
@check_master
def delete_citizenship(id):
    citizenship = Citizenship.query.get_or_404(id)
    db.session.delete(citizenship)
    flash('гражданство удалено')
    return redirect(url_for('.citizenships_list'))


@structure.route('/delete_section/<int:id>')
@login_required
@check_master
def delete_section(id):
    section = Section.query.get_or_404(id)
    db.session.delete(section)
    flash('секция удалена')
    return redirect(url_for('.sections_list'))


@structure.route('/delete_school/<int:id>')
@login_required
@check_master
def delete_school(id):
    school = School.query.get_or_404(id)
    db.session.delete(school)
    flash('школа удалена')
    return redirect(url_for('.schools_list'))


@structure.route('/delete_parent/<int:id>')
@login_required
@check_master
def delete_parent(id):
    parent = Parent.query.get_or_404(id)
    db.session.delete(parent)
    flash('родитель удален')
    return redirect(url_for('.parents_list'))


@structure.route('/delete_group/<int:id>')
@login_required
@check_master
def delete_group(id):
    group = Group.query.get_or_404(id)
    db.session.delete(group)
    flash('группа удалено')
    return redirect(url_for('.groups_list'))
