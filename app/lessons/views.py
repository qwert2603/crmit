from flask import request, render_template, abort, flash, url_for, redirect
from flask_login import login_required, current_user

from app import db
from app.decorators import check_master_or_teacher
from app.init_model import role_teacher_name
from app.lessons import lessons
from app.lessons.utils import payments_dicts, lessons_lists, dates_of_lessons_dict
from app.models import Lesson, Group, Payment, StudentInGroup, Attending
from app.utils import get_month_name, parse_date_or_none, number_of_month


# todo: lessons list screen (with filter by teacher / group).

@lessons.route('/<int:group_id>')
@login_required
@check_master_or_teacher
def lessons_list(group_id):
    group = Group.query.get_or_404(group_id)
    page = request.args.get('page', 1, type=int)
    pagination = group.lessons.order_by(Lesson.date.desc()).paginate(page, per_page=20, error_out=False)
    dates_of_lessons = dates_of_lessons_dict(group_id)
    months = [{'month_number': month_number, 'month_name': get_month_name(month_number),
               'lessons_dates': dates_of_lessons.get(month_number)}
              for month_number in range(group.start_month, group.end_month + 1)]
    return render_template('lessons/lessons_list.html', group=group, pagination=pagination, lessons=pagination.items,
                           months=months)


@lessons.route('/<int:group_id>/<int:month_number>', methods=['GET', 'POST'])
@login_required
@check_master_or_teacher
def lessons_in_month(group_id, month_number):
    group = Group.query.get_or_404(group_id)
    if month_number < group.start_month or month_number > group.end_month:
        abort(404)
    month_name = get_month_name(month_number)
    students_in_group = group.students_in_group_in_month(month_number)
    if 'submit' in request.form:
        ps = Payment.query \
            .join(StudentInGroup, StudentInGroup.id == Payment.student_in_group_id) \
            .filter(StudentInGroup.group_id == group_id, Payment.month == month_number)
        payments = dict()
        for p in ps:
            payments[p.student_in_group_id] = p
        for student_in_group in students_in_group:
            new_value = request.form.get('p_{}'.format(student_in_group.id), 0, type=int)
            if new_value < 0: new_value = 0
            max_value = group.section.price - student_in_group.discount
            if new_value > max_value: new_value = max_value
            payment = payments.get(student_in_group.id)
            is_cash = 'c_{}'.format(student_in_group.id) in request.form
            if payment is not None:
                if not payment.confirmed:
                    payment.value = new_value
                    payment.cash = is_cash
            else:
                db.session.add(Payment(student_in_group=student_in_group, month=month_number, value=new_value,
                                       cash=is_cash))
            ls = Lesson.lessons_in_group_in_month(group_id, month_number).all()
            for l in ls:
                new_date = parse_date_or_none(request.form.get('l_{}'.format(l.id)))
                if new_date is not None:
                    l.date = new_date
            attendings = dict()
            for l in ls:
                attendings[l.id] = dict()
                for a in l.attendings:
                    attendings[l.id][a.student_id] = a
            for l in ls:
                for student_in_group in students_in_group:
                    new_was = 'a_{}_{}'.format(l.id, student_in_group.student_id) in request.form
                    attending = attendings[l.id].get(student_in_group.student_id)
                    if attending is not None:
                        attending.was = new_was
                    else:
                        db.session.add(Attending(lesson=l, student=student_in_group.student, was=new_was))
        flash('посещения и оплата в группе {} за {} сохранены.'.format(group.name, month_name))
        return redirect(url_for('lessons.lessons_in_month', group_id=group_id, month_number=month_number))
    pd = payments_dicts(group_id, month_number)
    ll = lessons_lists(group_id, month_number)
    # todo: removable_lessons = dict().
    return render_template('lessons/lessons_in_month.html', group=group, month_name=month_name,
                           students_in_group=students_in_group, payments=pd[0], confirmed=pd[1], cash=pd[2],
                           lessons=ll[0], lesson_ids=ll[1], attendings=ll[2])


@lessons.route('/create/<int:group_id>', methods=['GET', 'POST'])
@login_required
@check_master_or_teacher
def create_lesson(group_id):
    group = Group.query.get_or_404(group_id)
    if current_user.system_role.name == role_teacher_name:
        if current_user.teacher.id != group.teacher_id:
            abort(403)

    if 'submit' in request.form:
        date = parse_date_or_none(request.form.get('date'))
        db.session.add(Lesson(group_id=group_id, teacher_id=group.teacher_id, date=date))
        flash('занятие создано: {}'.format(date.date()))
        return redirect(url_for('.lessons_in_month', group_id=group_id, month_number=number_of_month(date)))
    return render_template('lessons/create_lesson.html', group=group)
