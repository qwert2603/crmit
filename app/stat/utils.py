from sqlalchemy import func, or_

from app import db
from app.models import Lesson, Payment, StudentInGroup, Group


def group_students_count_by_month_dict(group_id):
    group = Group.query.get(group_id)
    result = dict()
    for m in range(group.start_month, group.end_month + 1):
        result[m] = group.students_in_month(m).count()
    return result


def group_payments_count_by_month_dict(group_id):
    pays_by_month = db.session.query(Payment.month, func.count(Payment.id)) \
        .join(StudentInGroup, StudentInGroup.id == Payment.student_in_group_id) \
        .filter(StudentInGroup.group_id == group_id, or_(Payment.value > 0, Payment.confirmed == True)) \
        .group_by(Payment.month) \
        .all()
    result = dict()
    for p in pays_by_month:
        result[p[0]] = p[1]
    return result


def group_payments_confirmed_count_by_month_dict(group_id):
    pays_by_month = db.session.query(Payment.month, func.count(Payment.id)) \
        .join(StudentInGroup, StudentInGroup.id == Payment.student_in_group_id) \
        .filter(StudentInGroup.group_id == group_id, Payment.confirmed == True) \
        .group_by(Payment.month) \
        .all()
    result = dict()
    for p in pays_by_month:
        result[p[0]] = p[1]
    return result


def group_attendings_percent_by_month_dict(group_id):
    group = Group.query.get(group_id)
    result = dict()
    for month_number in range(group.start_month, group.end_month + 1):
        students_in_month = group.students_in_month(month_number).count()
        if students_in_month == 0 or Lesson.lessons_in_group_in_month(group_id, month_number).count() == 0:
            continue
        was_count = 0
        lessons = Lesson.lessons_in_group_in_month(group_id, month_number).all()
        for l in lessons:
            was_count += l.attendings_was.count()
        result[month_number] = 100 * was_count // (students_in_month * len(lessons))
    return result
