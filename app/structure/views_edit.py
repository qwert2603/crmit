from flask import render_template, redirect, url_for, flash
from flask_login import login_required
from app.decorators import check_master, check_master_or_teacher
from app.models import Citizenship, Section, Parent, School, Group
from app.structure import structure
from app.structure.forms import CitizenshipForm, SectionForm, ParentForm, SchoolForm, GroupForm
from app.structure.utils import delete_unconfirmed_payments_out_of_months_period, \
    correct_student_enter_exit_month_to_group_period
from app.utils import year_from_month_number, month_from_month_number


@structure.route('/section/<int:id>', methods=['GET', 'POST'])
@login_required
@check_master
def edit_section(id):
    section = Section.query.get_or_404(id)
    form = SectionForm(section)
    if form.validate_on_submit():
        section.name = form.name.data
        section.price = form.price.data
        flash('секция {} изменена'.format(form.name.data))
        return redirect(url_for('.sections_list'))
    if not form.is_submitted():
        form.name.data = section.name
        form.price.data = section.price
    return render_template('structure/form_add_edit.html', form=form, class_name='секции', creating=False)


@structure.route('/citizenship/<int:id>', methods=['GET', 'POST'])
@login_required
@check_master
def edit_citizenship(id):
    citizenship = Citizenship.query.get_or_404(id)
    form = CitizenshipForm(citizenship)
    if form.validate_on_submit():
        citizenship.name = form.name.data
        flash('гражданство {} изменено'.format(form.name.data))
        return redirect(url_for('.citizenships_list'))
    if not form.is_submitted():
        form.name.data = citizenship.name
    return render_template('structure/form_add_edit.html', form=form, class_name='гражданства', creating=False)


@structure.route('/school/<int:id>', methods=['GET', 'POST'])
@login_required
@check_master
def edit_school(id):
    school = School.query.get_or_404(id)
    form = SchoolForm(school)
    if form.validate_on_submit():
        school.name = form.name.data
        flash('школа {} изменена'.format(form.name.data))
        return redirect(url_for('.schools_list'))
    if not form.is_submitted():
        form.name.data = school.name
    return render_template('structure/form_add_edit.html', form=form, class_name='школы', creating=False)


@structure.route('/parent/<int:id>', methods=['GET', 'POST'])
@login_required
@check_master_or_teacher
def edit_parent(id):
    parent = Parent.query.get_or_404(id)
    form = ParentForm(parent)
    if form.validate_on_submit():
        parent.fio = form.fio.data
        parent.phone = form.phone.data
        parent.email = form.email.data
        parent.passport = form.passport.data
        parent.address = form.address.data
        parent.home_phone = form.home_phone.data
        flash('родитель {} изменен'.format(form.fio.data))
        return redirect(url_for('.parents_list'))
    if not form.is_submitted():
        form.fio.data = parent.fio
        form.phone.data = parent.phone
        form.email.data = parent.email
        form.passport.data = parent.passport
        form.address.data = parent.address
        form.home_phone.data = parent.home_phone
    return render_template('structure/form_add_edit.html', form=form, class_name='родителя', creating=False)


@structure.route('/group/<int:id>', methods=['GET', 'POST'])
@login_required
@check_master
def edit_group(id):
    group = Group.query.get_or_404(id)
    form = GroupForm(group)
    if form.validate_on_submit():
        group.name = form.name.data
        group.teacher_id = form.teacher.data
        group.section_id = form.section.data
        group.start_month = form.start_month()
        group.end_month = form.end_month()
        correct_student_enter_exit_month_to_group_period(group)
        delete_unconfirmed_payments_out_of_months_period(group)
        flash('группа {} изменена'.format(form.name.data))
        return redirect(url_for('.groups_list'))
    if not form.is_submitted():
        form.name.data = group.name
        form.teacher.data = group.teacher_id
        form.section.data = group.section_id
        form.start_y.data = year_from_month_number(group.start_month)
        form.start_m.data = month_from_month_number(group.start_month) + 1
        form.end_y.data = year_from_month_number(group.end_month)
        form.end_m.data = month_from_month_number(group.end_month) + 1
    return render_template('structure/form_add_edit.html', form=form, class_name='группы', creating=False)
