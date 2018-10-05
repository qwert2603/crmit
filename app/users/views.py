from flask import render_template, redirect, request, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user

from app import db
from app.decorators import check_master_or_teacher, check_master
from app.init_model import role_master_name, role_teacher_name, developer_login
from app.models import SystemUser, Student
from app.users import users
from app.users.forms import LoginForm, ChangePasswordForm, ForceChangePasswordForm


@users.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = SystemUser.query.filter(SystemUser.login == form.login.data).first()
        if user is not None and user.verify_password(form.password.data):
            if user.enabled:
                user.force_ask_to_login = False
                login_user(user, form.remember_me.data)
                return redirect(request.args.get('next') or url_for('main.index'))
            else:
                flash('ваш аккаунт был отключен!')
                return redirect(url_for('.login'))
        flash('неверный логин или пароль!')
    return render_template('users/login.html', form=form)


@users.route('/logout')
@login_required
def logout():
    logout_user()
    flash('вы вышли из системы')
    return redirect(url_for('.login'))


@users.route('/logout_app')
@login_required
@check_master_or_teacher
def logout_app():
    for at in current_user.access_tokens.all():
        db.session.delete(at)
    flash('все ваши сессии в мобильном приложении завершены')
    return redirect(url_for('main.index'))


@users.route('/change_password', methods=['GET', 'POST'])
@login_required
@check_master_or_teacher
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.new_password.data
            db.session.add(current_user._get_current_object())
            flash('пароль изменен.')
            return redirect(url_for('main.index'))
        flash('неверный старый пароль!')
    return render_template('users/change_password.html', form=form)


@users.route('/force_change_password/<int:system_user_id>', methods=['GET', 'POST'])
@login_required
@check_master
def force_change_password(system_user_id):
    system_user = SystemUser.query.get_or_404(system_user_id)
    if system_user.system_role.name != role_master_name and system_user.system_role.name != role_teacher_name:
        flash('пароль ученика менять нельзя!')
        return redirect(url_for('main.index'))
    if system_user_id == current_user.id:
        return redirect(url_for('main.index'))
    if system_user.login == developer_login:
        return redirect(url_for('users.masters_list'))
    form = ForceChangePasswordForm()
    if form.validate_on_submit():
        system_user.password = form.new_password.data
        system_user.force_ask_to_login = True
        for at in system_user.access_tokens.all():
            db.session.delete(at)
        db.session.add(system_user)
        flash('пароль пользователя {} изменен.'.format(system_user.login))
        return redirect(url_for('main.index'))
    return render_template('users/force_change_password.html', form=form, system_user=system_user)


@users.route('/student_details/<int:id>')
@login_required
@check_master_or_teacher
def student_details(id):
    student = Student.query.get_or_404(id)
    return render_template('users/student_details.html', student=student)
