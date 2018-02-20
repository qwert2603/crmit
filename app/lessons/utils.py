from app import db
from app.models import Lesson, Payment, StudentInGroup
from app.utils import number_of_month
from config import DB_TYPE_POSTGRES, DB_TYPE


def lessons_lists(group_id, month_number):
    lessons = Lesson.lessons_in_group_in_month(group_id, month_number) \
        .order_by(Lesson.date) \
        .all()
    lesson_ids = []
    attendings = dict()
    for l in lessons:
        lesson_ids += [l.id]
        attendings[l.id] = dict()
        for a in l.attendings:
            attendings[l.id][a.student_id] = a.was
    return [lessons, lesson_ids, attendings]


def payments_dicts(group):
    values = dict()
    confirmed = dict()
    cash = dict()
    for m in range(group.start_month, group.end_month + 1):
        in_month_dicts = payments_in_month_dicts(group.id, m)
        values[m] = in_month_dicts[0]
        confirmed[m] = in_month_dicts[1]
        cash[m] = in_month_dicts[2]
    return [values, confirmed, cash]


def payments_in_month_dicts(group_id, month_number):
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


def removable_lessons_dict(group_id, month_number):
    removable = dict()
    for l in Lesson.lessons_in_group_in_month(group_id, month_number):
        if l.attendings_was.count() == 0:
            removable[l.id] = True
    return removable


def dates_of_lessons_dict(group_id):
    if DB_TYPE == DB_TYPE_POSTGRES:
        sql = '''
                    SELECT
                        extract(YEAR FROM date)                                         AS year,
                        extract(MONTH FROM date)                                        AS month,
                        string_agg(extract(DAY FROM date) :: TEXT, ' / ' ORDER BY date) AS dates
                    FROM lessons
                    WHERE group_id = {}
                    GROUP BY month, year
        '''.format(group_id)
    else:
        sql = '''
                SELECT
                    extract(YEAR FROM date) AS year,
                    extract(MONTH FROM date) AS month,
                    GROUP_CONCAT(CAST(extract(DAY FROM date) as CHAR) ORDER BY date SEPARATOR ' / ') AS dates
                    FROM lessons
                WHERE group_id = {}
                GROUP BY month, year
        '''.format(group_id)

    rows = db.engine.execute(sql)
    result = dict()
    for row in rows:
        result[number_of_month(row['year'], row['month'] - 1)] = row['dates']
    return result
