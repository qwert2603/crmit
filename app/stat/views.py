from flask import render_template
from flask_login import login_required

from app.decorators import check_master_or_teacher
from app.models import Group, Lesson
from app.stat import stat
from app.stat.utils import group_students_count_by_month_dict, group_payments_count_by_month_dict, \
    group_payments_confirmed_count_by_month_dict, group_attendings_percent_by_month_dict
from app.utils import get_month_name


@stat.route('/group/<int:group_id>')
@login_required
@check_master_or_teacher
def group_stat(group_id):
    group = Group.query.get_or_404(group_id)
    students_by_month = group_students_count_by_month_dict(group_id)
    pays_by_month = group_payments_count_by_month_dict(group_id)
    pays_confirmed_by_month = group_payments_confirmed_count_by_month_dict(group_id)
    attendings_percent_by_month = group_attendings_percent_by_month_dict(group_id)
    months = [{'month_number': month_number, 'month_name': get_month_name(month_number),
               'students_count': students_by_month.get(month_number),
               'lessons_count': Lesson.lessons_in_group_in_month(group_id, month_number).count(),
               'attendings_percent': attendings_percent_by_month.get(month_number, 0),
               'payments': pays_by_month.get(month_number, 0),
               'payments_confirmed': pays_confirmed_by_month.get(month_number, 0)}
              for month_number in range(group.start_month, group.end_month + 1)]
    return render_template('stat/group.html', group=group, months=months)
