from sqlalchemy import func

from app import db
from app.models import Payment, StudentInGroup, Group


class PaymentsInGroupInfo:
    def __init__(self):
        # key in dicts is student_in_group_id.
        self.values = dict()
        self.confirmed = dict()
        self.cash = dict()
        self.comments = dict()
        self.confirmed_count_students = dict()
        self.non_zero_count_students = dict()

        # key in dicts is month_number.
        self.confirmed_count_months = dict()
        self.non_zero_count_months = dict()


def payments_info(group: Group) -> PaymentsInGroupInfo:
    result = PaymentsInGroupInfo()

    students_in_group = group.students_in_group.all()
    for s in students_in_group:
        result.confirmed_count_students[s.id] = 0
        result.non_zero_count_students[s.id] = 0
    for m in range(group.start_month, group.end_month + 1):
        in_month_dicts = payments_in_month_info(group.id, m)
        result.values[m] = in_month_dicts.values
        result.confirmed[m] = in_month_dicts.confirmed
        result.cash[m] = in_month_dicts.cash
        result.comments[m] = in_month_dicts.comments
        result.confirmed_count_months[m] = 0
        result.non_zero_count_months[m] = 0
        for s in students_in_group:
            if result.confirmed.get(m, dict()).get(s.id):
                result.confirmed_count_students[s.id] += 1
                result.confirmed_count_months[m] += 1
            if result.confirmed.get(m, dict()).get(s.id) or result.values.get(m, dict()).get(s.id, 0) > 0:
                result.non_zero_count_students[s.id] += 1
                result.non_zero_count_months[m] += 1
    return result


class PaymentsInGroupInMonthInfo:
    def __init__(self):
        # key in dicts is student_in_group_id.
        self.values = dict()
        self.confirmed = dict()
        self.cash = dict()
        self.comments = dict()


def payments_in_month_info(group_id: int, month_number: int) -> PaymentsInGroupInMonthInfo:
    result = PaymentsInGroupInMonthInfo()

    ps = Payment.query \
        .join(StudentInGroup, StudentInGroup.id == Payment.student_in_group_id) \
        .filter(StudentInGroup.group_id == group_id, Payment.month == month_number)

    for p in ps:
        result.values[p.student_in_group_id] = p.value
        result.confirmed[p.student_in_group_id] = p.confirmed
        result.cash[p.student_in_group_id] = p.cash
        result.comments[p.student_in_group_id] = p.comment
    return result


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
