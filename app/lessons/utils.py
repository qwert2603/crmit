from app.models import Lesson, Payment, StudentInGroup
from app.utils import start_date_of_month, end_date_of_month


def payments_dicts(group_id, month_number):
    ps = Payment.query \
        .join(StudentInGroup, StudentInGroup.id == Payment.student_in_group_id) \
        .filter(StudentInGroup.group_id == group_id, Payment.month == month_number)
    values = dict()
    confirmed = dict()
    cash = dict()
    for p in ps:
        values[p.student_in_group_id] = p.value
        confirmed[p.student_in_group_id] = p.confirmed
        cash[p.student_in_group_id] = p.cash
    return [values, confirmed, cash]


def lessons_lists(group_id, month_number):
    lessons = Lesson.query \
        .filter(Lesson.group_id == group_id,
                Lesson.date >= start_date_of_month(month_number),
                Lesson.date <= end_date_of_month(month_number)) \
        .order_by(Lesson.date) \
        .all()
    lesson_ids = []
    lesson_dates = []
    attendings = dict()
    for l in lessons:
        lesson_ids += [l.id]
        lesson_dates += [l.date]
        attendings[l.id] = dict()
        for a in l.attendings:
            attendings[l.id][a.student_id] = a.was
    return [lesson_ids, lesson_dates, attendings]
