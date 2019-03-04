from flask import flash, abort
from flask_login import login_required

from app import db
from app.decorators import check_master, check_master_or_teacher, check_developer
from app.is_removable_check import is_master_removable, is_teacher_removable, is_student_removable, \
    is_developer_removable
from app.models import Master, Teacher, Student, Bot, Developer
from app.users import users
from app.users.utils import delete_all_messages_with_user
from app.utils import redirect_back_or_home


@users.route('/delete_master/<int:id>')
@login_required
@check_master
def delete_master(id):
    master = Master.query.get_or_404(id)
    if not is_master_removable(master): abort(409)
    for at in master.system_user.access_tokens.all():
        db.session.delete(at)
    master.system_user.notifications.delete()
    delete_all_messages_with_user(master.system_user_id)
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
    teacher.system_user.notifications.delete()
    delete_all_messages_with_user(teacher.system_user_id)
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
    delete_all_messages_with_user(student.system_user_id)
    db.session.delete(student)
    db.session.delete(student.system_user)
    flash('ученик {} удалён'.format(student.fio))
    return redirect_back_or_home()


@users.route('/delete_bot/<int:id>')
@login_required
@check_developer
def delete_bot(id):
    bot = Bot.query.get_or_404(id)
    for at in bot.system_user.access_tokens.all():
        db.session.delete(at)
    delete_all_messages_with_user(bot.system_user_id)
    db.session.delete(bot)
    db.session.delete(bot.system_user)
    flash('бот {} удалён'.format(bot.fio))
    return redirect_back_or_home()


@users.route('/delete_developer/<int:id>')
@login_required
@check_developer
def delete_developer(id):
    developer = Developer.query.get_or_404(id)
    if not is_developer_removable(developer): abort(409)
    for at in developer.system_user.access_tokens.all():
        db.session.delete(at)
    delete_all_messages_with_user(developer.system_user_id)
    db.session.delete(developer)
    db.session.delete(developer.system_user)
    flash('разработчик {} удалён'.format(developer.fio))
    return redirect_back_or_home()
