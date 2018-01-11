from flask import render_template, redirect, url_for, flash
from flask_login import login_required

from app import db
from app.decorators import check_master, check_master_or_teacher
from app.init_model import role_master_name, role_teacher_name, role_student_name
from app.models import SystemUser, SystemRole, Master, Teacher, Student, ParentOfStudent
from app.users import users
from app.users.forms import RegistrationMasterForm, RegistrationTeacherForm, RegistrationStudentForm


@users.route('/register/master', methods=['GET', 'POST'])
@login_required
@check_master
def register_master():
    form = RegistrationMasterForm()
    if form.validate_on_submit():
        role_master = SystemRole.query.filter_by(name=role_master_name).first()
        user_master = SystemUser(login=form.login.data, password=form.password.data, system_role=role_master)
        master = Master(fio=form.fio.data, system_user=user_master)
        db.session.add(user_master)
        db.session.add(master)
        flash('мастер {} создан.'.format(form.login.data))
        return redirect(url_for('main.index'))
    return render_template('users/register.html', form=form, role_name='руководителя')


@users.route('/register/teacher', methods=['GET', 'POST'])
@login_required
@check_master
def register_teacher():
    form = RegistrationTeacherForm()
    if form.validate_on_submit():
        role_teacher = SystemRole.query.filter_by(name=role_teacher_name).first()
        user_teacher = SystemUser(login=form.login.data, password=form.password.data, system_role=role_teacher)
        teacher = Teacher(fio=form.fio.data, system_user=user_teacher)
        db.session.add(user_teacher)
        db.session.add(teacher)
        flash('преподаватель {} создан.'.format(form.login.data))
        return redirect(url_for('main.index'))
    return render_template('users/register.html', form=form, role_name='преподавателя')


@users.route('/register/student', methods=['GET', 'POST'])
@login_required
@check_master_or_teacher
def register_student():
    form = RegistrationStudentForm()
    if form.validate_on_submit():
        role_student = SystemRole.query.filter_by(name=role_student_name).first()
        user_student = SystemUser(login=form.login.data, password=form.password.data, system_role=role_student)
        student = Student(fio=form.fio.data, system_user=user_student, birth_date=form.birth_date.data,
                          birth_place=form.birth_place.data, registration_place=form.registration_place.data,
                          actual_address=form.actual_address.data, additional_info=form.additional_info.data,
                          known_from=form.known_from.data, school_id=form.school.data,
                          citizenship_id=form.citizenship.data)
        if form.mother.data != -1:
            db.session.add(ParentOfStudent(student=student, parent_id=form.mother.data))
        if form.father.data != -1:
            db.session.add(ParentOfStudent(student=student, parent_id=form.father.data))
        db.session.add(user_student)
        db.session.add(student)
        flash('ученик {} создан.'.format(form.login.data))
        return redirect(url_for('main.index'))
    return render_template('users/register.html', form=form, role_name='ученика')
