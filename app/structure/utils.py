from sqlalchemy import func, or_
from app import db
from app.models import Payment, StudentInGroup, Lesson
from app.utils import number_of_month, compare_not_none


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
    return compare_not_none(min, min_payment_month, min_lesson_month)


def min_end_month_number_group(group_id):
    max_payment_month = db.session.query(func.max(Payment.month)) \
        .join(StudentInGroup, StudentInGroup.id == Payment.student_in_group_id) \
        .filter(StudentInGroup.group_id == group_id) \
        .filter(Payment.confirmed == True) \
        .scalar()
    max_lesson_date = db.session.query(func.max(Lesson.date)) \
        .filter(Lesson.group_id == group_id) \
        .scalar()
    max_lesson_month = None
    if max_lesson_date is not None: max_lesson_month = number_of_month(max_lesson_date)
    return compare_not_none(max, max_payment_month, max_lesson_month)


# from app.structure.utils import max_start_month_number_group

def delete_unconfirmed_payments_out_of_months_period(group):
    unconfirmed = Payment.query \
        .join(StudentInGroup, StudentInGroup.id == Payment.student_in_group_id) \
        .filter(StudentInGroup.group_id == group.id) \
        .filter(Payment.confirmed == False) \
        .filter(or_(Payment.month < group.start_month, Payment.month > group.end_month)) \
        .all()
    for p in unconfirmed:
        db.session.delete(p)
