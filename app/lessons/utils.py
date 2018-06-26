from app import db
from app.models import Lesson
from app.utils import number_of_month
from config import DB_TYPE_POSTGRES


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


def dates_of_lessons_dict(group_id):
    from manage import app
    if app.config['DB_TYPE'] == DB_TYPE_POSTGRES:
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
                         WHERE attendings.was = TRUE) a ON a.lesson_id = lessons.id
              JOIN groups ON groups.id = lessons.group_id
            WHERE lessons.date < date(now())
            GROUP BY lessons.id, groups.name
            HAVING count(a.id) = 0
            ORDER BY lesson_date DESC
            LIMIT 100
    '''
    rows = db.engine.execute(sql)
    result = []
    for row in rows:
        result.append(PastEmptyLesson(row[0], row[1], row[2]))
    return result
