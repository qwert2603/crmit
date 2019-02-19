from flask import request, render_template
from flask_login import login_required, current_user

from app.decorators import check_student
from app.models import Lesson, Group, StudentInGroup
from app.student import student
from app.utils import parse_date_or_none, start_date_of_month, end_date_of_month


@student.route('/lessons')
@login_required
@check_student
def lessons():
    group_id = request.args.get('group_id', 0, type=int)
    selected_date = parse_date_or_none(request.args.get('selected_date'))
    page = request.args.get('page', 1, type=int)

    sigs = current_user.student.students_in_groups
    if group_id > 0: sigs = sigs.filter(StudentInGroup.group_id == group_id)

    lessons_queries = [
        sig.group.lessons
            .filter(Lesson.date >= start_date_of_month(sig.enter_month),
                    Lesson.date <= end_date_of_month(sig.exit_month))
        for sig in sigs
    ]

    pagination = Lesson.query.filter(False)

    for q in lessons_queries:
        pagination = pagination.union(q)

    if selected_date is not None: pagination = pagination.filter(Lesson.date <= selected_date)
    pagination = pagination.order_by(Lesson.date.desc())
    pagination = pagination.paginate(page, per_page=20, error_out=False)

    groups = current_user.student.groups \
        .order_by(Group.start_month.desc(), Group.name) \
        .all()

    return render_template('student/lessons_list.html', group_id=group_id, selected_date=selected_date,
                           pagination=pagination, lessons=pagination.items, groups=groups)


@student.route('/payments')
@login_required
@check_student
def payments():
    return 'payments'


@student.route('/messages')
@login_required
@check_student
def messages():
    return 'messages'
