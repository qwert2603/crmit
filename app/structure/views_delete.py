from flask import render_template, redirect, url_for, flash
from flask_login import login_required

from app import db
from app.decorators import check_master, check_master_or_teacher
from app.models import Citizenship, Section, Parent, School, Group
from app.structure import structure


@structure.route('/delete_citizenship/<int:id>')
@login_required
@check_master
def delete_citizenship(id):
    return


@structure.route('/delete_section/<int:id>')
@login_required
@check_master
def delete_section(id):
    return


@structure.route('/delete_school/<int:id>')
@login_required
@check_master
def delete_school(id):
    return


@structure.route('/delete_parent/<int:id>')
@login_required
@check_master
def delete_parent(id):
    return


@structure.route('/delete_group/<int:id>')
@login_required
@check_master
def delete_group(id):
    return