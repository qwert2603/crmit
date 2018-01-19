from flask import render_template, redirect, request, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user

from app import db
from app.models import SystemUser
from app.users import users
from app.users.forms import LoginForm, ChangePasswordForm
from app.decorators import check_master_or_teacher


@users.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = SystemUser.query.filter(SystemUser.login == form.login.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('неверный логин или пароль!')
    return render_template('users/login.html', form=form)


@users.route('/logout')
@login_required
def logout():
    logout_user()
    flash('вы вышли из системы')
    return redirect(url_for('.login'))


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

