from flask import render_template, redirect, url_for, flash
from flask_login import login_required
from app.decorators import check_master, check_master_or_teacher
from app.models import Master, Teacher, Student, ParentOfStudent
from app.users import users
from app.users.forms import RegistrationMasterForm, RegistrationTeacherForm, RegistrationStudentForm
from app.utils import password_from_date


@users.route('/master/<int:id>', methods=['GET', 'POST'])
@login_required
@check_master
def edit_master(id):
    master = Master.query.get_or_404(id)
    form = RegistrationMasterForm(master)
    if form.validate_on_submit():
        master.fio = form.fio.data
        master.system_user.login = form.login.data
        flash('руководитель {} изменен'.format(form.fio.data))
        return redirect(url_for('.masters_list'))
    if not form.is_submitted():
        form.login.data = master.system_user.login
        form.fio.data = master.fio
    return render_template('users/form_register_edit.html', form=form, class_name='мастера', creating=False)


@users.route('/teacher/<int:id>', methods=['GET', 'POST'])
@login_required
@check_master
def edit_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    form = RegistrationTeacherForm(teacher)
    if form.validate_on_submit():
        teacher.fio = form.fio.data
        teacher.system_user.login = form.login.data
        flash('преподаватель {} изменен'.format(form.fio.data))
        return redirect(url_for('.teachers_list'))
    if not form.is_submitted():
        form.login.data = teacher.system_user.login
        form.fio.data = teacher.fio
    return render_template('users/form_register_edit.html', form=form, class_name='преподавателя', creating=False)


@users.route('/student/<int:id>', methods=['GET', 'POST'])
@login_required
@check_master_or_teacher
def edit_student(id):
    student = Student.query.get_or_404(id)
    mother = student.mother
    father = student.father
    mother_id = None
    father_id = None
    if mother: mother_id = mother.id
    if father: father_id = father.id
    form = RegistrationStudentForm(student)
    if form.validate_on_submit():
        student.fio = form.fio.data
        student.system_user.login = form.login.data
        student.system_user.password = password_from_date(form.birth_date.data)
        student.birth_date = form.birth_date.data
        student.birth_place = form.birth_place.data
        student.registration_place = form.registration_place.data
        student.actual_address = form.actual_address.data
        student.additional_info = form.additional_info.data
        student.known_from = form.known_from.data
        student.school_id = form.school.data
        student.citizenship_id = form.citizenship.data
        new_mother_id = form.mother.data
        if new_mother_id == -1: new_mother_id = None
        new_father_id = form.father.data
        if new_father_id == -1: new_father_id = None
        ParentOfStudent.change_parent(student.id, mother_id, new_mother_id, True)
        ParentOfStudent.change_parent(student.id, father_id, new_father_id, False)
        flash('ученик {} изменен'.format(form.fio.data))
        return redirect(url_for('.students_list'))
    if not form.is_submitted():
        form.login.data = student.system_user.login
        form.fio.data = student.fio
        form.birth_date.data = student.birth_date
        form.birth_place.data = student.birth_place
        form.registration_place.data = student.registration_place
        form.actual_address.data = student.actual_address
        form.additional_info.data = student.additional_info
        form.known_from.data = student.known_from
        form.school.data = student.school_id
        form.citizenship.data = student.citizenship_id
        form.mother.data = mother_id
        form.father.data = father_id
    return render_template('users/form_register_edit.html', form=form, class_name='ученика', creating=False)
