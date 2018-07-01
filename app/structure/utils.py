from sqlalchemy import func, or_
from app import db
from app.models import Payment, StudentInGroup, Lesson, Attending, attending_was, attending_was_not, \
    attending_was_not_ill
from app.utils import number_of_month_for_date, compare_not_none, start_date_of_month, end_date_of_month


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
    if min_lesson_date is not None: min_lesson_month = number_of_month_for_date(min_lesson_date)
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
    if max_lesson_date is not None: max_lesson_month = number_of_month_for_date(max_lesson_date)
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


def correct_student_enter_exit_month_to_group_period(group):
    for student_in_group in group.students_in_group.all():
        if student_in_group.enter_month < group.start_month: student_in_group.enter_month = group.start_month
        if student_in_group.exit_month > group.end_month: student_in_group.exit_month = group.end_month


# s=StudentInGroup.query.get(7)

def max_enter_month_number_student_in_group(student_in_group):
    min_payment_month = db.session.query(func.min(Payment.month)) \
        .join(StudentInGroup, StudentInGroup.id == Payment.student_in_group_id) \
        .filter(StudentInGroup.id == student_in_group.id) \
        .filter(Payment.confirmed == True) \
        .scalar()
    min_attending_date = db.session.query(func.min(Lesson.date)) \
        .filter(Lesson.group_id == student_in_group.group_id) \
        .join(Attending, Attending.lesson_id == Lesson.id) \
        .filter(Attending.student_id == student_in_group.student_id, Attending.state == attending_was) \
        .scalar()
    min_attending_month = None
    if min_attending_date is not None: min_attending_month = number_of_month_for_date(min_attending_date)
    return compare_not_none(min, min_payment_month, min_attending_month)


def min_exit_month_number_student_in_group(student_in_group):
    max_payment_month = db.session.query(func.max(Payment.month)) \
        .join(StudentInGroup, StudentInGroup.id == Payment.student_in_group_id) \
        .filter(StudentInGroup.id == student_in_group.id) \
        .filter(Payment.confirmed == True) \
        .scalar()
    max_attending_date = db.session.query(func.max(Lesson.date)) \
        .filter(Lesson.group_id == student_in_group.group_id) \
        .join(Attending, Attending.lesson_id == Lesson.id) \
        .filter(Attending.student_id == student_in_group.student_id, Attending.state == attending_was) \
        .scalar()
    max_attending_month = None
    if max_attending_date is not None: max_attending_month = number_of_month_for_date(max_attending_date)
    return compare_not_none(max, max_payment_month, max_attending_month)


def delete_unconfirmed_payments_out_of_months_period_student(student_in_group):
    unconfirmed = student_in_group.payments \
        .filter(Payment.confirmed == False) \
        .filter(or_(Payment.month < student_in_group.enter_month, Payment.month > student_in_group.exit_month)) \
        .all()
    for p in unconfirmed:
        db.session.delete(p)


def delete_attendings_was_not_out_of_months_period_student(student_in_group):
    attendings_was_not = Attending.query \
        .filter(Attending.student_id == student_in_group.student_id) \
        .filter(or_(Attending.state == attending_was_not, Attending.state == attending_was_not_ill)) \
        .join(Lesson, Lesson.id == Attending.lesson_id) \
        .filter(Lesson.group_id == student_in_group.group_id) \
        .filter(or_(Lesson.date < start_date_of_month(student_in_group.enter_month),
                    Lesson.date > end_date_of_month(student_in_group.exit_month))) \
        .all()
    for a in attendings_was_not:
        db.session.delete(a)
