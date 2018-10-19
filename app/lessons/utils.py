import datetime

from app import db
from app.models import Lesson, attending_was
from app.utils import number_of_month, end_date_of_month, start_date_of_month
from config import DB_TYPE_POSTGRES


def lessons_lists(group_id, month_number):
    lessons = Lesson.lessons_in_group_in_month(group_id, month_number) \
        .order_by(Lesson.date) \
        .all()
    attendings_states = dict()
    for l in lessons:
        attendings_states[l.id] = dict()
        for a in l.attendings:
            attendings_states[l.id][a.student_id] = a.state
    return [lessons, attendings_states]


def dates_of_lessons_dict(group_id):
    from app_holder import app_instance
    if app_instance.config['DB_TYPE'] == DB_TYPE_POSTGRES:
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


class PastEmptyLesson:
    def __init__(self, id, date, group_name):
        self.id = id
        self.date = date
        self.group_name = group_name


def empty_past_lessons():
    sql = '''
            SELECT
              lessons.id   lesson_id,
              lessons.date lesson_date,
              groups.name  group_name
            FROM lessons
              LEFT JOIN (SELECT *
                         FROM attendings
                         WHERE attendings.state = {}) a ON a.lesson_id = lessons.id
              JOIN groups ON groups.id = lessons.group_id
            WHERE lessons.date < date(now())
            GROUP BY lessons.id, groups.name
            HAVING count(a.id) = 0
            ORDER BY lesson_date DESC
            LIMIT 100
    '''.format(attending_was)
    rows = db.engine.execute(sql)
    result = []
    for row in rows:
        result.append(PastEmptyLesson(row[0], row[1], row[2]))
    return result


def fill_group_by_schedule(group, new_dows):
    existing_lessons = group.lessons.filter(Lesson.date > datetime.date.today()).all()
    for lesson in existing_lessons:
        for a in lesson.attendings:
            db.session.delete(a)
        db.session.delete(lesson)
    start_date_1 = datetime.date.today() + datetime.timedelta(days=1)
    start_date_2 = start_date_of_month(group.start_month)
    for date in days_of_dows(start_date=max(start_date_1, start_date_2), end_date=end_date_of_month(group.end_month),
                             dows=new_dows):
        db.session.add(Lesson(group_id=group.id, teacher_id=group.teacher_id, date=date))


def days_of_dows(start_date, end_date, dows):
    result = []
    date = start_date
    while date <= end_date:
        if date.weekday() in dows:
            result.append(date)
        date = date + datetime.timedelta(days=1)
    return result

# from app.lessons.utils import days_of_dows
# import datetime

# days_of_dows(datetime.datetime.strptime('01062018', "%d%m%Y"), datetime.datetime.strptime('31072018', "%d%m%Y"),
#              {1, 4, 5})
