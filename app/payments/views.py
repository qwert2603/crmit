from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user

from app import db
from app.decorators import check_access_group_write
from app.models import Group, Payment
from app.payments import payments
from app.payments.utils import payments_info, get_sum_not_confirmed_teacher, get_sum_not_confirmed_by_group


@payments.route('/group/<int:group_id>', methods=['GET', 'POST'])
@login_required
@check_access_group_write()
def payments_in_group(group_id):
    group = Group.query.get_or_404(group_id)
    can_confirm = current_user.is_master
    if 'submit' in request.form:
        for month_number in range(group.start_month, group.end_month + 1):
            ps = group.payments_in_month(month_number)
            payments = dict()
            for p in ps:
                payments[p.student_in_group_id] = p
            for student_in_group in group.students_in_group_in_month(month_number):
                new_value = request.form.get('p_{}_{}'.format(month_number, student_in_group.id), 0, type=int)
                if new_value < 0: new_value = 0
                max_value = group.section.price - student_in_group.discount
                if new_value > max_value: new_value = max_value
                payment = payments.get(student_in_group.id)
                is_cash = 'cash_{}_{}'.format(month_number, student_in_group.id) in request.form
                is_confirmed = 'conf_{}_{}'.format(month_number, student_in_group.id) in request.form
                comment = request.form.get('comment_{}_{}'.format(month_number, student_in_group.id), '')
                if payment is not None:
                    if not payment.confirmed:
                        payment.value = new_value
                        payment.cash = is_cash
                        payment.comment = comment
                    if can_confirm: payment.confirmed = is_confirmed
                else:
                    db.session.add(Payment(student_in_group=student_in_group, month=month_number, value=new_value,
                                           cash=is_cash, confirmed=can_confirm and is_confirmed, comment=comment))
        flash('оплата в группе {} сохранена.'.format(group.name))
        return redirect(url_for('payments.payments_in_group', group_id=group_id))
    pd = payments_info(group)
    total_payments = 0
    confirmed_payments = 0
    non_zero_payments = 0
    students_in_month = dict()
    for month_number in range(group.start_month, group.end_month + 1):
        students_count = group.students_in_group_in_month(month_number).count()
        total_payments += students_count
        confirmed_payments += pd.confirmed_count_months[month_number]
        non_zero_payments += pd.non_zero_count_months[month_number]
        students_in_month[month_number] = students_count
    if current_user.is_teacher:
        sum_not_confirmed_by_group = get_sum_not_confirmed_by_group(current_user.teacher.id)
        sum_not_confirmed_all = get_sum_not_confirmed_teacher(current_user.teacher.id)
    else:
        sum_not_confirmed_by_group = None
        sum_not_confirmed_all = None
    students_in_group = group.students_in_group_by_fio.all()
    return render_template('payments/payments_in_group.html', group=group, students_in_group=students_in_group,
                           payments=pd.values, confirmed=pd.confirmed, cash=pd.cash, comments=pd.comments,
                           confirmed_count_months=pd.confirmed_count_months,
                           confirmed_count_students=pd.confirmed_count_students,
                           non_zero_count_months=pd.non_zero_count_months,
                           non_zero_count_students=pd.non_zero_count_students, total_payments=total_payments,
                           confirmed_payments=confirmed_payments, non_zero_payments=non_zero_payments,
                           students_in_month=students_in_month, can_confirm=can_confirm,
                           sum_not_confirmed_by_group=sum_not_confirmed_by_group,
                           sum_not_confirmed_all=sum_not_confirmed_all)
