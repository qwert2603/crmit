from flask import render_template, redirect, url_for, flash
from flask_login import login_required

from app import db
from app.decorators import check_master, check_master_or_teacher
from app.models import Citizenship, Section, Parent, School, Group
from app.structure import structure
from app.structure.forms import CitizenshipForm, SectionForm, ParentForm, SchoolForm, GroupForm


@structure.route('/citizenship', methods=['GET', 'POST'])
@login_required
@check_master
def add_citizenship():
    form = CitizenshipForm()
    if form.validate_on_submit():
        db.session.add(Citizenship(name=form.name.data))
        flash('гражданство {} создано'.format(form.name.data))
        return redirect(url_for('main.index'))
    return render_template('structure/form_add_edit.html', form=form, class_name='гражданства', creating=True)


@structure.route('/section', methods=['GET', 'POST'])
@login_required
@check_master
def add_section():
    form = SectionForm()
    if form.validate_on_submit():
        db.session.add(Section(name=form.name.data, price=form.price.data))
        flash('секция {} создана'.format(form.name.data))
        return redirect(url_for('main.index'))
    return render_template('structure/form_add_edit.html', form=form, class_name='секции', creating=True)


@structure.route('/school', methods=['GET', 'POST'])
@login_required
@check_master
def add_school():
    form = SchoolForm()
    if form.validate_on_submit():
        db.session.add(School(name=form.name.data))
        flash('школа {} создана'.format(form.name.data))
        return redirect(url_for('main.index'))
    return render_template('structure/form_add_edit.html', form=form, class_name='школы', creating=True)


@structure.route('/parent', methods=['GET', 'POST'])
@login_required
@check_master_or_teacher
def add_parent():
    form = ParentForm()
    if form.validate_on_submit():
        db.session.add(Parent(fio=form.fio.data, phone=form.phone.data, email=form.email.data,
                              passport=form.passport.data, address=form.address.data, home_phone=form.home_phone.data))
        flash('родитель {} создан'.format(form.fio.data))
        return redirect(url_for('main.index'))
    return render_template('structure/form_add_edit.html', form=form, class_name='родителя', creating=True)


@structure.route('/group', methods=['GET', 'POST'])
@login_required
@check_master
def add_group():
    form = GroupForm()
    if form.validate_on_submit():
        db.session.add(Group(name=form.name.data, section_id=form.section.data, teacher_id=form.teacher.data,
                             start_month=form.start_month(), end_month=form.end_month()))
        flash('группа {} создана'.format(form.name.data))
        return redirect(url_for('main.index'))
    return render_template('structure/form_add_edit.html', form=form, class_name='группы', creating=True)
