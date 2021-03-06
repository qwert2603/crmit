from flask import render_template, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.decorators import check_master, check_master_or_teacher, check_developer
from app.models import Master, Teacher, Student, ParentOfStudent, Parent, Bot, Developer
from app.users import users
from app.users.forms import RegistrationMasterForm, RegistrationTeacherForm, RegistrationStudentForm, \
    create_new_parent_id, no_parent_id, RegistrationBotForm
from app.utils import password_from_date, notification_types_list_to_int


@users.route('/master/<int:id>', methods=['GET', 'POST'])
@login_required
@check_master
def edit_master(id):
    master = Master.query.get_or_404(id)
    form = RegistrationMasterForm(master)
    if form.validate_on_submit():
        master.fio = form.fio.data
        master.system_user.login = form.login.data
        if master.system_user_id == current_user.id and not form.enabled.data:
            flash('вы не можете отключить себя!')
        else:
            master.system_user.enabled = form.enabled.data
        flash('руководитель {} изменен'.format(form.fio.data))
        return redirect(url_for('.masters_list'))
    if not form.is_submitted():
        form.login.data = master.system_user.login
        form.fio.data = master.fio
        form.enabled.data = master.system_user.enabled
    return render_template('users/form_register_edit.html', form=form, class_name='руководителя', creating=False)


@users.route('/teacher/<int:id>', methods=['GET', 'POST'])
@login_required
@check_master
def edit_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    form = RegistrationTeacherForm(teacher)
    if form.validate_on_submit():
        teacher.fio = form.fio.data
        teacher.phone = form.phone.data
        teacher.system_user.login = form.login.data
        teacher.system_user.enabled = form.enabled.data
        flash('преподаватель {} изменен'.format(form.fio.data))
        return redirect(url_for('.teachers_list'))
    if not form.is_submitted():
        form.login.data = teacher.system_user.login
        form.fio.data = teacher.fio
        form.phone.data = teacher.phone
        form.enabled.data = teacher.system_user.enabled
    return render_template('users/form_register_edit.html', form=form, class_name='преподавателя', creating=False)


@users.route('/bot/<int:id>', methods=['GET', 'POST'])
@login_required
@check_developer
def edit_bot(id):
    bot = Bot.query.get_or_404(id)
    form = RegistrationBotForm(bot)
    if form.validate_on_submit():
        bot.fio = form.fio.data
        bot.system_user.login = form.login.data
        bot.system_user.enabled = form.enabled.data
        flash('бот {} изменен'.format(form.fio.data))
        return redirect(url_for('.bots_list'))
    if not form.is_submitted():
        form.login.data = bot.system_user.login
        form.fio.data = bot.fio
        form.enabled.data = bot.system_user.enabled
    return render_template('users/form_register_edit.html', form=form, class_name='бота', creating=False)


@users.route('/developer/<int:id>', methods=['GET', 'POST'])
@login_required
@check_developer
def edit_developer(id):
    developer = Developer.query.get_or_404(id)
    form = RegistrationBotForm(developer)
    if form.validate_on_submit():
        developer.fio = form.fio.data
        developer.system_user.login = form.login.data
        developer.system_user.enabled = form.enabled.data
        flash('разработчик {} изменен'.format(form.fio.data))
        return redirect(url_for('.developers_list'))
    if not form.is_submitted():
        form.login.data = developer.system_user.login
        form.fio.data = developer.fio
        form.enabled.data = developer.system_user.enabled
    return render_template('users/form_register_edit.html', form=form, class_name='разработчика', creating=False)


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

        if student.system_user.verify_password(password_from_date(student.birth_date)):
            student.system_user.password = password_from_date(form.birth_date.data)
            student.system_user.force_ask_to_login = True

        student.system_user.enabled = form.enabled.data
        student.birth_date = form.birth_date.data
        student.birth_place = form.birth_place.data
        student.registration_place = form.registration_place.data
        student.actual_address = form.actual_address.data
        student.additional_info = form.additional_info.data
        student.known_from = form.known_from.data
        student.school_id = form.school.data
        student.citizenship_id = form.citizenship.data
        student.grade = form.grade.data
        student.shift = form.shift.data
        student.phone = form.phone.data
        student.contact_phone = form.contact_phone.data
        student.filled = True

        new_mother_id = form.mother.data
        if new_mother_id == no_parent_id: new_mother_id = None
        new_father_id = form.father.data
        if new_father_id == no_parent_id: new_father_id = None

        if new_mother_id == create_new_parent_id:
            mother = Parent(fio=form.m_fio.data, phone=form.m_phone.data, email=form.m_email.data,
                            passport=form.m_passport.data, address=form.m_address.data,
                            home_phone=form.m_home_phone.data, vk_link=form.m_vk_link.data,
                            notification_types=notification_types_list_to_int(form.m_notification_types.data))
            db.session.add(mother)
            ParentOfStudent.change_parent(student_id=student.id, is_mother=True, new_parent_id=None, new_parent=mother)
            flash('родитель {} создан'.format(form.m_fio.data))
        else:
            ParentOfStudent.change_parent(student_id=student.id, is_mother=True, new_parent_id=new_mother_id,
                                          new_parent=None)

        if new_father_id == create_new_parent_id:
            father = Parent(fio=form.f_fio.data, phone=form.f_phone.data, email=form.f_email.data,
                            passport=form.f_passport.data, address=form.f_address.data,
                            home_phone=form.f_home_phone.data, vk_link=form.f_vk_link.data,
                            notification_types=notification_types_list_to_int(form.f_notification_types.data))
            db.session.add(father)
            ParentOfStudent.change_parent(student_id=student.id, is_mother=False, new_parent_id=None, new_parent=father)
            flash('родитель {} создан'.format(form.f_fio.data))
        else:
            ParentOfStudent.change_parent(student_id=student.id, is_mother=False, new_parent_id=new_father_id,
                                          new_parent=None)

        flash('ученик {} изменен'.format(form.fio.data))
        return redirect(url_for('.students_list'))
    if not form.is_submitted():
        form.login.data = student.system_user.login
        form.fio.data = student.fio
        form.enabled.data = student.system_user.enabled
        form.birth_date.data = student.birth_date
        form.birth_place.data = student.birth_place
        form.registration_place.data = student.registration_place
        form.actual_address.data = student.actual_address
        form.additional_info.data = student.additional_info
        form.known_from.data = student.known_from
        form.school.data = student.school_id
        form.grade.data = student.grade
        form.shift.data = student.shift
        form.phone.data = student.phone
        form.contact_phone.data = student.contact_phone
        form.citizenship.data = student.citizenship_id
        form.mother.data = mother_id
        form.father.data = father_id
    return render_template('users/form_register_edit.html', form=form, class_name='ученика', creating=False)
