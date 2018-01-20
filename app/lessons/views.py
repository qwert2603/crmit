from flask import request, render_template, abort
from flask_login import login_required

from app.decorators import check_master_or_teacher
from app.lessons import lessons
from app.models import Lesson, Group, Payment, StudentInGroup
from app.utils import group_start_month, group_end_month, get_month_name, start_date_of_month, end_date_of_month


@lessons.route('/<int:group_id>')
@login_required
@check_master_or_teacher
def lessons_list(group_id):
    group = Group.query.get_or_404(group_id)
    page = request.args.get('page', 1, type=int)
    pagination = group.lessons.order_by(Lesson.date.desc()).paginate(page, per_page=20, error_out=False)
    return render_template('lessons/lessons_list.html', group=group, pagination=pagination, items=pagination.items)


@lessons.route('/<int:group_id>/<int:month_number>', methods=['GET', 'POST'])
@login_required
@check_master_or_teacher
def lessons_in_month(group_id, month_number):
    group = Group.query.get_or_404(group_id)
    if month_number < group_start_month(group.start_year) or month_number > group_end_month(group.start_year):
        abort(404)
    students_in_group = group.students_in_group_in_month(month_number)
    # todo: functions for creating dicts (payments / confirmed / lesson_ids ...).
    ps = Payment.query \
        .join(StudentInGroup, StudentInGroup.id == Payment.student_in_group_id) \
        .filter(StudentInGroup.group_id == group_id, Payment.month == month_number)
    payments = {}
    confirmed = {}
    for p in ps:
        payments[p.student_in_group_id] = p.value
        confirmed[p.student_in_group_id] = p.confirmed
    lessons = Lesson.query \
        .filter(Lesson.group_id == group_id,
                Lesson.date >= start_date_of_month(month_number),
                Lesson.date <= end_date_of_month(month_number)) \
        .order_by(Lesson.date) \
        .all()
    lesson_ids = []
    lesson_dates = []
    attendings = {}
    for l in lessons:
        lesson_ids += [l.id]
        lesson_dates += [l.date]
        attendings[l.id] = {}
        for a in l.attendings:
            attendings[l.id][a.student_id] = a.was
    return render_template('lessons/lessons_in_month.html', group=group, month_name=get_month_name(month_number),
                           students_in_group=students_in_group, payments=payments, confirmed=confirmed,
                           lesson_ids=lesson_ids, lesson_dates=lesson_dates, attendings=attendings)
