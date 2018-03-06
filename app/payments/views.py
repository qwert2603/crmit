from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from app import db
from app.decorators import check_access_group_write
from app.init_model import role_master_name
from app.lessons.utils import payments_dicts
from app.models import Group, StudentInGroup, Student, Payment
from app.payments import payments


@payments.route('/group/<int:group_id>', methods=['GET', 'POST'])
@login_required
@check_access_group_write()
def payments_in_group(group_id):
    group = Group.query.get_or_404(group_id)
    students_in_group = group.students_in_group \
        .join(Student, Student.id == StudentInGroup.student_id) \
        .order_by(Student.fio) \
        .all()
    can_confirm = current_user.system_role.name == role_master_name
    if 'submit' in request.form:
        for month_number in range(group.start_month, group.end_month + 1):
            ps = Payment.query \
                .join(StudentInGroup, StudentInGroup.id == Payment.student_in_group_id) \
                .filter(StudentInGroup.group_id == group_id, Payment.month == month_number)
            payments = dict()
            for p in ps:
                payments[p.student_in_group_id] = p
            for student_in_group in students_in_group:
                new_value = request.form.get('p_{}_{}'.format(month_number, student_in_group.id), 0, type=int)
                if new_value < 0: new_value = 0
                max_value = group.section.price - student_in_group.discount
                if new_value > max_value: new_value = max_value
                payment = payments.get(student_in_group.id)
                is_cash = 'cash_{}_{}'.format(month_number, student_in_group.id) in request.form
                is_confirmed = 'conf_{}_{}'.format(month_number, student_in_group.id) in request.form
                if payment is not None:
                    if not payment.confirmed:
                        payment.value = new_value
                        payment.cash = is_cash
                    if can_confirm: payment.confirmed = is_confirmed
                else:
                    db.session.add(Payment(student_in_group=student_in_group, month=month_number, value=new_value,
                                           cash=is_cash, confirmed=can_confirm and is_confirmed))
        db.session.commit()
        flash('оплата в группе {} сохранена.'.format(group.name))
        return redirect(url_for('payments.payments_in_group', group_id=group_id))
    pd = payments_dicts(group)
    total_payments = 0
    confirmed_payments = 0
    students_in_month = dict()
    for month_number in range(group.start_month, group.end_month + 1):
        students_count = group.students_in_group_in_month(month_number).count()
        total_payments += students_count
        confirmed_payments += pd[3][month_number]
        students_in_month[month_number] = students_count
    return render_template('payments/payments_in_group.html', group=group, students_in_group=students_in_group,
                           payments=pd[0], confirmed=pd[1], cash=pd[2], confirmed_count_months=pd[3],
                           confirmed_count_students=pd[4], total_payments=total_payments,
                           confirmed_payments=confirmed_payments, students_in_month=students_in_month,
                           can_confirm=can_confirm)
