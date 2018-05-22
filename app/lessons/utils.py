from app import db
from app.models import Lesson, Payment, StudentInGroup
from app.utils import number_of_month
from config import DB_TYPE_POSTGRES, DB_TYPE


def lessons_lists(group_id, month_number):
    lessons = Lesson.lessons_in_group_in_month(group_id, month_number) \
        .order_by(Lesson.date) \
        .all()
    attendings = dict()
    for l in lessons:
        attendings[l.id] = dict()
        for a in l.attendings:
            attendings[l.id][a.student_id] = a.was
    return [lessons, attendings]


def payments_dicts(group):
    values = dict()
    confirmed = dict()
    cash = dict()
    confirmed_count_months = dict()
    confirmed_count_students = dict()
    students_in_group = group.students_in_group.all()
    for s in students_in_group:
        confirmed_count_students[s.id] = 0
    for m in range(group.start_month, group.end_month + 1):
        in_month_dicts = payments_in_month_dicts(group.id, m)
        values[m] = in_month_dicts[0]
        confirmed[m] = in_month_dicts[1]
        cash[m] = in_month_dicts[2]
        confirmed_count_months[m] = 0
        for s in students_in_group:
            if confirmed.get(m, dict()).get(s.id):
                confirmed_count_students[s.id] += 1
                confirmed_count_months[m] += 1
    return [values, confirmed, cash, confirmed_count_months, confirmed_count_students]


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
        result[number_of_month(row[0], row[1] - 1)] = row[2]
    return result
