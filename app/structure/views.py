from flask import render_template, request, url_for, redirect, flash
from flask_login import login_required
from app.decorators import check_master_or_teacher
from app.models import Group, Student, StudentInGroup
from app.structure import structure
from app import db
from app.structure.utils import max_enter_month_number_student_in_group, min_exit_month_number_student_in_group, \
    delete_attendings_was_not_out_of_months_period_student, delete_unconfirmed_payments_out_of_months_period_student


@structure.route('/students_in_group/<int:id>', methods=['GET', 'POST'])
@login_required
@check_master_or_teacher
def students_in_group(id):
    group = Group.query.get_or_404(id)
    students_in_group = group.students_in_group.all()
    in_group_students_ids = [s.student.id for s in students_in_group]
    if 'submit' in request.form:
        form_in_group = [int(i) for i in request.form.getlist('in_group')]
        print(in_group_students_ids)
        print(form_in_group)
        for new_id in form_in_group:
            if new_id not in in_group_students_ids:
                db.session.add(StudentInGroup(student_id=new_id, group_id=id, enter_month=group.start_month,
                                              exit_month=group.end_month))
        for old_student_in_group in students_in_group:
            if old_student_in_group.student.id not in form_in_group:
                if old_student_in_group.attendings_was.count() > 0:
                    flash('нельзя удалить {} из группы {}, так как он посещал занятия!'.format(
                        old_student_in_group.student.fio,
                        group.name))
                elif old_student_in_group.payments_confirmed.count() > 0:
                    flash('нельзя удалить {} из группы {}, так как он вносил подтвержденную оплату!'.format(
                        old_student_in_group.student.fio,
                        group.name))
                else:
                    old_student_in_group.payments_not_confirmed.delete()
                    for a in old_student_in_group.attendings_was_not.all():
                        db.session.delete(a)
                    db.session.delete(old_student_in_group)
        flash('список учеников в группе {} изменен.'.format(group.name))
        return redirect(url_for('structure.groups_list'))
    other_students = Student.query \
        .filter(Student.id.notin_(in_group_students_ids)) \
        .order_by(Student.fio).all()
    return render_template('structure/students_in_group.html', group=group, students_in_group=students_in_group,
                           other_students=other_students)


@structure.route('/discounts/<int:id>', methods=['GET', 'POST'])
@login_required
@check_master_or_teacher
def discounts(id):
    group = Group.query.get_or_404(id)
    students_in_group = group.students_in_group.all()
    if 'submit' in request.form:
        for student_in_group in students_in_group:
            new_discount = request.form.get('d_{}'.format(student_in_group.id), 0, type=int)
            if new_discount is not None:
                if new_discount > group.section.price:
                    flash('скидка не может быть больше стоимости({})'.format(student_in_group.student.fio))
                elif new_discount < 0:
                    flash('скидка не может быть меньше нуля! ({})'.format(student_in_group.student.fio))
                else:
                    student_in_group.discount = new_discount
            new_enter_month_number = request.form.get('enter_{}'.format(student_in_group.id), 0, type=int)
            if new_enter_month_number is not None:
                if new_enter_month_number < group.start_month:
                    flash('ученик не может войти раньше начала группы ({})'.format(student_in_group.student.fio))
                elif new_enter_month_number > group.end_month:
                    flash('ученик не может войти позже конца группы ({})'.format(student_in_group.student.fio))
                elif new_enter_month_number > (max_enter_month_number_student_in_group(student_in_group) or 999999):
                    flash('ученик не может войти позже посещения или оплаты ({})'.format(student_in_group.student.fio))
                else:
                    student_in_group.enter_month = new_enter_month_number
            new_exit_month_number = request.form.get('exit_{}'.format(student_in_group.id), 0, type=int)
            if new_exit_month_number is not None:
                if new_exit_month_number < group.start_month:
                    flash('ученик не может выйти раньше начала группы ({})'.format(student_in_group.student.fio))
                elif new_exit_month_number > group.end_month:
                    flash('ученик не может выйти позже конца группы ({})'.format(student_in_group.student.fio))
                elif new_exit_month_number < (min_exit_month_number_student_in_group(student_in_group) or -1):
                    flash('ученик не может выйти раньше посещения или оплаты ({})'.format(student_in_group.student.fio))
                else:
                    student_in_group.exit_month = new_exit_month_number
            delete_unconfirmed_payments_out_of_months_period_student(student_in_group)
            delete_attendings_was_not_out_of_months_period_student(student_in_group)
        flash('скидки и месяцы входа/выхода в группе {} изменены.'.format(group.name))
        return redirect(url_for('structure.groups_list'))
    return render_template('structure/discounts.html', group=group, students_in_group=students_in_group)
