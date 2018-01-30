from sqlalchemy import func
from app import db
from app.models import Payment, StudentInGroup, Lesson, Group
from app.utils import number_of_month


def max_start_month_number_group(group_id):
    min_payment_month = db.session.query(func.min(Payment.month)) \
        .join(StudentInGroup, StudentInGroup.id == Payment.student_in_group_id) \
        .filter(StudentInGroup.group_id == group_id) \
        .filter(Payment.confirmed == True) \
        .scalar()
    min_lesson_date = db.session.query(func.min(Lesson.date)) \
        .filter(Lesson.group_id == group_id) \
        .scalar()
    min_lesson_month = None
    if min_lesson_date is not None: min_lesson_month = number_of_month(min_lesson_date)
    if min_payment_month is None and min_lesson_month is None: return None
    if min_payment_month is None: return min_lesson_month
    if min_lesson_month is None: return min_payment_month
    return min(min_payment_month, min_lesson_month)


def min_end_month_number_group(group_id):
    max_payment_month = db.session.query(func.max(Payment.month)) \
        .join(StudentInGroup, StudentInGroup.id == Payment.student_in_group_id) \
        .filter(StudentInGroup.group_id == group_id) \
        .filter(Payment.confirmed == True) \
        .scalar()
    #todo
    return max_payment_month

# from app.structure.utils import max_start_month_number_group
