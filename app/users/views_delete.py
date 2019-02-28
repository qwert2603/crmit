from flask import flash, abort
from flask_login import login_required

from app import db
from app.decorators import check_master, check_master_or_teacher
from app.init_model import developer_login
from app.is_removable_check import is_master_removable, is_teacher_removable, is_student_removable
from app.models import Master, Teacher, Student, Bot
from app.users import users
from app.utils import redirect_back_or_home


@users.route('/delete_master/<int:id>')
@login_required
@check_master
def delete_master(id):
    master = Master.query.get_or_404(id)
    if master.system_user.login == developer_login:
        abort(404)
    if not is_master_removable(master): abort(409)
    for at in master.system_user.access_tokens.all():
        db.session.delete(at)
    db.session.delete(master)
    db.session.delete(master.system_user)
    flash('руководитель {} удалён'.format(master.fio))
    return redirect_back_or_home()


@users.route('/delete_teacher/<int:id>')
@login_required
@check_master
def delete_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    if not is_teacher_removable(teacher): abort(409)
    for at in teacher.system_user.access_tokens.all():
        db.session.delete(at)
    db.session.delete(teacher)
    db.session.delete(teacher.system_user)
    flash('преподаватель {} удалён'.format(teacher.fio))
    return redirect_back_or_home()


@users.route('/delete_student/<int:id>')
@login_required
@check_master_or_teacher
def delete_student(id):
    student = Student.query.get_or_404(id)
    if not is_student_removable(student): abort(409)
    for at in student.system_user.access_tokens.all():
        db.session.delete(at)
    student.parent_of_students.delete()
    db.session.delete(student)
    db.session.delete(student.system_user)
    flash('ученик {} удалён'.format(student.fio))
    return redirect_back_or_home()


@users.route('/delete_bot/<int:id>')
@login_required
@check_master
def delete_bot(id):
    bot = Bot.query.get_or_404(id)
    for at in bot.system_user.access_tokens.all():
        db.session.delete(at)
    db.session.delete(bot)
    db.session.delete(bot.system_user)
    flash('бот {} удалён'.format(bot.fio))
    return redirect_back_or_home()
