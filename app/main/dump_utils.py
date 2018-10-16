import datetime

from app.models import Section, Payment, Lesson
from app.utils import get_month_name


def payment_to_dump(payment):
    return {
        'id': payment.id,
        'month': get_month_name(payment.month),
        'value': payment.value,
        'cash': payment.cash,
        'confirmed': payment.confirmed,
        'comment': payment.comment,
    }


def student_in_group_to_dump(student_in_group):
    return {
        'student_in_group_id': student_in_group.id,
        'student_id': student_in_group.student.id,
        'fio': student_in_group.student.fio,
        'discount': student_in_group.discount,
        'payments': [payment_to_dump(p) for p in student_in_group.payments.order_by(Payment.month).all()]
    }


_attending_states_strings = ['не был', 'был', 'болел']


def attending_to_dump(attending):
    return {
        'student_fio': attending.student.fio,
        'state': _attending_states_strings[attending.state]
    }


def lesson_to_dump(lesson):
    return {
        'id': lesson.id,
        'date': lesson.date.strftime("%Y-%m-%d"),
        'attendings': [attending_to_dump(a) for a in lesson.attendings.all()]
    }


def group_to_dump(group):
    return {
        'id': group.id,
        'name': group.name,
        'teacher_fio': group.teacher.fio,
        'students': [student_in_group_to_dump(s) for s in group.students_in_group.all()],
        'lessons': [lesson_to_dump(le) for le in group.lessons.order_by(Lesson.date).all()]
    }


def section_to_dump(section):
    return {
        'id': section.id,
        'name': section.name,
        'groups': [group_to_dump(g) for g in section.groups.all()]
    }


def db_to_dump():
    return {
        'created_at': datetime.datetime.utcnow(),
        'sections': [section_to_dump(s) for s in Section.query.all()]
    }
