import datetime

from app.models import Section, Payment, Lesson, Attending
from app.utils import get_month_name


def db_to_dump():

    attendings_map = dict()
    for a in Attending.query.all():
        attendings_of_lesson = attendings_map.get(a.lesson_id)
        if attendings_of_lesson is None:
            attendings_of_lesson = list()
            attendings_map[a.lesson_id] = attendings_of_lesson
        attendings_of_lesson.append(a)

    payments_map = dict()
    for p in Payment.query.order_by(Payment.month).all():
        payments_of_sig = payments_map.get(p.student_in_group)
        if payments_of_sig is None:
            payments_of_sig = list()
            payments_map[p.student_in_group] = payments_of_sig
            payments_of_sig.append(p)

    _attending_states_strings = ['не был', 'был', 'болел']

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
            'payments': [payment_to_dump(p) for p in payments_map.get(student_in_group.id) or list()]
        }

    def attending_to_dump(attending):
        return {
            'student_fio': attending.student.fio,
            'state': _attending_states_strings[attending.state]
        }

    def lesson_to_dump(lesson):
        return {
            'id': lesson.id,
            'date': lesson.date.strftime("%Y-%m-%d"),
            'attendings': [attending_to_dump(a) for a in attendings_map.get(lesson.id) or list()]
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

    return {
        'created_at': datetime.datetime.utcnow(),
        'sections': [section_to_dump(s) for s in Section.query.all()]
    }
