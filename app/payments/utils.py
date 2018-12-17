from sqlalchemy import func

from app import db
from app.models import Payment, StudentInGroup, Group


# todo: return class.
def payments_dicts(group):
    values = dict()
    confirmed = dict()
    cash = dict()
    comments = dict()
    confirmed_count_months = dict()
    confirmed_count_students = dict()
    non_zero_count_months = dict()
    non_zero_count_students = dict()
    students_in_group = group.students_in_group.all()
    for s in students_in_group:
        confirmed_count_students[s.id] = 0
        non_zero_count_students[s.id] = 0
    for m in range(group.start_month, group.end_month + 1):
        in_month_dicts = payments_in_month_dicts(group.id, m)
        values[m] = in_month_dicts[0]
        confirmed[m] = in_month_dicts[1]
        cash[m] = in_month_dicts[2]
        comments[m] = in_month_dicts[3]
        confirmed_count_months[m] = 0
        non_zero_count_months[m] = 0
        for s in students_in_group:
            if confirmed.get(m, dict()).get(s.id):
                confirmed_count_students[s.id] += 1
                confirmed_count_months[m] += 1
            if confirmed.get(m, dict()).get(s.id) or values.get(m, dict()).get(s.id, 0) > 0:
                non_zero_count_students[s.id] += 1
                non_zero_count_months[m] += 1
    return [values, confirmed, cash, comments, confirmed_count_months, confirmed_count_students,
            non_zero_count_months, non_zero_count_students]


def payments_in_month_dicts(group_id, month_number):
    ps = Payment.query \
        .join(StudentInGroup, StudentInGroup.id == Payment.student_in_group_id) \
        .filter(StudentInGroup.group_id == group_id, Payment.month == month_number)
    values = dict()
    confirmed = dict()
    cash = dict()
    comments = dict()
    for p in ps:
        values[p.student_in_group_id] = p.value
        confirmed[p.student_in_group_id] = p.confirmed
        cash[p.student_in_group_id] = p.cash
        comments[p.student_in_group_id] = p.comment
    return [values, confirmed, cash, comments]


def get_sum_not_confirmed_by_group(teacher_id):
    groups = Group.query \
        .filter_by(teacher_id=teacher_id) \
        .order_by(Group.start_month.desc(), Group.name) \
        .all()
    result = []
    for group in groups:
        result.append({'name': group.name, 'sum_not_confirmed': group.sum_not_confirmed})
    return result


def get_sum_not_confirmed_teacher(teacher_id):
    return db.session.query(func.sum(Payment.value)) \
        .join(StudentInGroup, StudentInGroup.id == Payment.student_in_group_id) \
        .join(Group, Group.id == StudentInGroup.group_id) \
        .filter(Group.teacher_id == teacher_id) \
        .filter(Payment.confirmed == False) \
        .scalar()
