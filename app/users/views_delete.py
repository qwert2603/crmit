from flask import flash, redirect, url_for, abort
from flask_login import login_required
from app import db
from app.is_removable_check import is_master_removable, is_teacher_removable, is_student_removable
from app.models import Master, Teacher, Student
from app.users import users
from app.decorators import check_master, check_master_or_teacher


@users.route('/delete_master/<int:id>')
@login_required
@check_master
def delete_master(id):
    master = Master.query.get_or_404(id)
    if not is_master_removable(master): abort(409)
    db.session.delete(master)
    db.session.delete(master.system_user)
    flash('руководитель удалён')
    return redirect(url_for('.masters_list'))


@users.route('/delete_teacher/<int:id>')
@login_required
@check_master
def delete_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    if not is_teacher_removable(teacher): abort(409)
    db.session.delete(teacher)
    db.session.delete(teacher.system_user)
    flash('преподаватель удалён')
    return redirect(url_for('.teachers_list'))


@users.route('/delete_student/<int:id>')
@login_required
@check_master_or_teacher
def delete_student(id):
    student = Student.query.get_or_404(id)
    if not is_student_removable(student): abort(409)
    db.session.delete(student)
    db.session.delete(student.system_user)
    flash('ученик удалён')
    return redirect(url_for('.students_list'))
