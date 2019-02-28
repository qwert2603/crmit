from flask import render_template, redirect, url_for, flash
from flask_login import login_required

from app import db
from app.decorators import check_master, check_master_or_teacher
from app.init_model import role_master_name, role_teacher_name, role_student_name, default_citizenship_id, role_bot_name
from app.models import SystemUser, SystemRole, Master, Teacher, Student, ParentOfStudent, Parent, StudentInGroup, Group, \
    contact_phone_student, Bot
from app.users import users
from app.users.forms import RegistrationMasterForm, RegistrationTeacherForm, RegistrationStudentForm, \
    RegistrationStudentFastForm, RegistrationBotForm
from app.users.forms import create_new_parent_id
from app.utils import generate_login_student, password_from_date, notification_types_list_to_int


@users.route('/register/master', methods=['GET', 'POST'])
@login_required
@check_master
def register_master():
    form = RegistrationMasterForm()
    if form.validate_on_submit():
        role_master = SystemRole.query.filter_by(name=role_master_name).first()
        user_master = SystemUser(login=form.login.data, password=form.password.data, system_role=role_master,
                                 enabled=form.enabled.data)
        master = Master(fio=form.fio.data, system_user=user_master)
        db.session.add(user_master)
        db.session.add(master)
        flash('руководитель {} создан.'.format(form.login.data))
        return redirect(url_for('.masters_list'))
    return render_template('users/form_register_edit.html', form=form, class_name='руководителя', creating=True)


@users.route('/register/teacher', methods=['GET', 'POST'])
@login_required
@check_master
def register_teacher():
    form = RegistrationTeacherForm()
    if form.validate_on_submit():
        role_teacher = SystemRole.query.filter_by(name=role_teacher_name).first()
        user_teacher = SystemUser(login=form.login.data, password=form.password.data, system_role=role_teacher,
                                  enabled=form.enabled.data)
        teacher = Teacher(fio=form.fio.data, system_user=user_teacher, phone=form.phone.data)
        db.session.add(user_teacher)
        db.session.add(teacher)
        flash('преподаватель {} создан.'.format(form.login.data))
        return redirect(url_for('.teachers_list'))
    return render_template('users/form_register_edit.html', form=form, class_name='преподавателя', creating=True)


@users.route('/register/bot', methods=['GET', 'POST'])
@login_required
@check_master
def register_bot():
    form = RegistrationBotForm()
    if form.validate_on_submit():
        role_bot = SystemRole.query.filter_by(name=role_bot_name).first()
        user_bot = SystemUser(login=form.login.data, password=form.password.data, system_role=role_bot,
                              enabled=form.enabled.data)
        bot = Bot(fio=form.fio.data, system_user=user_bot)
        db.session.add(user_bot)
        db.session.add(bot)
        flash('бот {} создан.'.format(form.login.data))
        return redirect(url_for('.bots_list'))
    return render_template('users/form_register_edit.html', form=form, class_name='бота', creating=True)


@users.route('/register/student', methods=['GET', 'POST'])
@login_required
@check_master_or_teacher
def register_student():
    form = RegistrationStudentForm()
    if form.validate_on_submit():
        fio = '{} {} {}'.format(form.last_name.data, form.first_name.data, form.second_name.data).strip()
        role_student = SystemRole.query.filter_by(name=role_student_name).first()
        user_student = SystemUser(
            login=generate_login_student(form.last_name.data, form.first_name.data, form.second_name.data),
            password=password_from_date(form.birth_date.data), system_role=role_student, enabled=form.enabled.data)
        student = Student(fio=fio, system_user=user_student, birth_date=form.birth_date.data,
                          birth_place=form.birth_place.data, registration_place=form.registration_place.data,
                          actual_address=form.actual_address.data, additional_info=form.additional_info.data,
                          known_from=form.known_from.data, school_id=form.school.data,
                          citizenship_id=form.citizenship.data, grade=form.grade.data, shift=form.shift.data,
                          phone=form.phone.data, contact_phone=form.contact_phone.data)
        if form.mother.data > 0:
            db.session.add(ParentOfStudent(student=student, parent_id=form.mother.data, is_mother=True))
        if form.father.data > 0:
            db.session.add(ParentOfStudent(student=student, parent_id=form.father.data, is_mother=False))
        if form.mother.data == create_new_parent_id:
            mother = Parent(fio=form.m_fio.data, phone=form.m_phone.data, email=form.m_email.data,
                            passport=form.m_passport.data, address=form.m_address.data,
                            home_phone=form.m_home_phone.data, vk_link=form.m_vk_link.data,
                            notification_types=notification_types_list_to_int(form.m_notification_types.data))
            db.session.add(mother)
            db.session.add(ParentOfStudent(student=student, parent=mother, is_mother=True))
            flash('родитель {} создан'.format(form.m_fio.data))
        if form.father.data == create_new_parent_id:
            father = Parent(fio=form.f_fio.data, phone=form.f_phone.data, email=form.f_email.data,
                            passport=form.f_passport.data, address=form.f_address.data,
                            home_phone=form.f_home_phone.data, vk_link=form.f_vk_link.data,
                            notification_types=notification_types_list_to_int(form.f_notification_types.data))
            db.session.add(father)
            db.session.add(ParentOfStudent(student=student, parent=father, is_mother=False))
            flash('родитель {} создан'.format(form.f_fio.data))
        db.session.add(user_student)
        db.session.add(student)
        flash('ученик {} создан.'.format(fio))
        return redirect(url_for('users.students_list'))
    return render_template('users/form_register_edit.html', form=form, class_name='ученика', creating=True)


@users.route('/register/student/fast/<int:group_id>/<int:month_number>', methods=['GET', 'POST'])
@users.route('/register/student/fast', methods=['GET', 'POST'])
@login_required
@check_master_or_teacher
def register_student_fast(group_id=None, month_number=None):
    form = RegistrationStudentFastForm()
    if form.validate_on_submit():
        na_text = 'не указано'
        fio = '{} {} {}'.format(form.last_name.data, form.first_name.data, form.second_name.data).strip()
        role_student = SystemRole.query.filter_by(name=role_student_name).first()
        user_student = SystemUser(
            login=generate_login_student(form.last_name.data, form.first_name.data, form.second_name.data),
            password=password_from_date(form.birth_date.data), system_role=role_student, enabled=True)
        additional_info = 'телефон родителя: {}; \nимя родителя: {}'.format(form.parent_phone.data,
                                                                            form.parent_name.data)
        student = Student(fio=fio, system_user=user_student, birth_date=form.birth_date.data,
                          birth_place=na_text, registration_place=na_text, actual_address=na_text,
                          additional_info=additional_info, known_from=na_text, school_id=form.school.data,
                          citizenship_id=default_citizenship_id, grade=form.grade.data, shift=form.shift.data,
                          phone=na_text, contact_phone=contact_phone_student, filled=False)
        db.session.add(user_student)
        db.session.add(student)
        if group_id is not None:
            group = Group.query.get_or_404(group_id)
            db.session.add(StudentInGroup(student=student, group=group, enter_month=group.start_month,
                                          exit_month=group.end_month))
            flash('ученик {} создан и добавлен в группу {}.'.format(fio, group.name))
            return redirect(url_for('lessons.lessons_in_month', group_id=group_id, month_number=month_number))
        else:
            flash('ученик {} создан.'.format(fio))
            return redirect(url_for('users.students_list'))
    return render_template('users/form_register_student_fast.html', form=form)
