from flask import render_template, redirect, request, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user

from app import db
from app.auth import auth
from app.auth.forms import LoginForm, RegistrationMasterForm, RegistrationTeacherForm, RegistrationStudentForm, \
    ChangePasswordForm
from app.models import SystemUser, SystemRole, Master, Teacher, Student, ParentOfStudent
from app.init_model import role_master_name, role_teacher_name, role_student_name
from app.decorators import check_master, check_master_or_teacher


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = SystemUser.query.filter(SystemUser.login == form.login.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('неверный логин или пароль!')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('вы вышли из системы')
    return redirect(url_for('.login'))


@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user._get_current_object())
            flash('пароль изменен.')
            return redirect(url_for('main.index'))
        flash('неверный старый пароль!')
    return render_template('auth/change_password.html', form=form)


@auth.route('/register/master', methods=['GET', 'POST'])
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
    return render_template('auth/register.html', form=form, role_name='руководителя')


@auth.route('/register/teacher', methods=['GET', 'POST'])
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
    return render_template('auth/register.html', form=form, role_name='преподавателя')


@auth.route('/register/student', methods=['GET', 'POST'])
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
    return render_template('auth/register.html', form=form, role_name='ученика')
