from flask import render_template, redirect, request, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from sqlalchemy import or_

from app import db
from . import auth
from .forms import LoginForm, RegistrationForm
from ..models import SystemUser, SystemRole


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = SystemUser.query.filter(or_(SystemUser.username == form.login.data, SystemUser.email == form.login.data)).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('wrong email or password!')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('u logged out')
    return redirect(url_for('.login'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = SystemUser(username=form.username.data, email=form.email.data,
                    password=form.password.data, role=SystemRole.query.get(1))
        db.session.add(user)
        db.session.commit()
        flash('and now u r going to login.')
        return redirect(url_for('.login'))
    return render_template('auth/register.html', form=form)

