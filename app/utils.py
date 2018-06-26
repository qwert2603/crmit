import datetime


def generate_login_student(last_name, first_name, second_name):
    login = ''
    login += translit(first_name[0])
    if len(second_name) > 0:
        login += translit(second_name[0])
    for c in last_name:
        login += translit(c)
    from app import SystemUser
    if not SystemUser.query.filter_by(login=login).first():
        return login
    else:
        suffix = 2
        while SystemUser.query.filter_by(login=login + str(suffix)).first():
            suffix = suffix + 1
        return login + str(suffix)


def translit(c):
    c = c.lower()
    if c == 'а': return 'a'
    if c == 'б': return 'b'
    if c == 'в': return 'v'
    if c == 'г': return 'g'
    if c == 'д': return 'd'
    if c == 'е': return 'e'
    if c == 'ё': return 'e'
    if c == 'ж': return 'zh'
    if c == 'з': return 'z'
    if c == 'и': return 'i'
    if c == 'й': return 'j'
    if c == 'к': return 'k'
    if c == 'л': return 'l'
    if c == 'м': return 'm'
    if c == 'н': return 'n'
    if c == 'о': return 'o'
    if c == 'п': return 'p'
    if c == 'р': return 'r'
    if c == 'с': return 's'
    if c == 'т': return 't'
    if c == 'у': return 'u'
    if c == 'ф': return 'f'
    if c == 'х': return 'h'
    if c == 'ц': return 'ts'
    if c == 'ч': return 'ch'
    if c == 'ш': return 'sh'
    if c == 'щ': return 'shch'
    if c == 'ъ': return ''
    if c == 'ы': return 'yi'
    if c == 'ь': return ''
    if c == 'э': return 'eh'
    if c == 'ю': return 'yu'
    if c == 'я': return 'ya'
    raise Exception('unknown letter "{}"'.format(c))


months_per_year = 12
earliest_year = 2017


def number_of_month_for_date(date):
    return (date.year - earliest_year) * months_per_year + date.month - 1


def number_of_month(year, month_in_year):
    return (year - earliest_year) * months_per_year + month_in_year


month_names = [
    'январь',
    'февраль',
    'март',
    'апрель',
    'май',
    'июнь',
    'июль',
    'август',
    'сентябрь',
    'октябрь',
    'ноябрь',
    'декабрь'
]

days_per_month = [31, 28, 31, 30,
                  31, 30, 31, 31,
                  30, 31, 30, 31]


def year_from_month_number(month_number):
    return month_number // months_per_year + earliest_year


def month_from_month_number(month_number):
    return month_number % months_per_year


def get_month_name(month_number):
    return '{} {}'.format(month_names[month_from_month_number(month_number)], year_from_month_number(month_number))


def start_date_of_month(month_number):
    return datetime.date(year_from_month_number(month_number), month_from_month_number(month_number) + 1, 1)


def end_date_of_month(month_number):
    year = year_from_month_number(month_number)
    month_of_year = month_from_month_number(month_number)
    day = days_per_month[month_of_year]
    if is_leap_year(year) and month_of_year == 1: day = day + 1
    return datetime.date(year, month_of_year + 1, day)


def is_leap_year(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def password_from_date(date):
    return '{:0>2}{:0>2}{:4}'.format(date.day, date.month, date.year)


def parse_date_or_none(date_str):
    try:
        return datetime.datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return None


def parse_int_or_none(int_str):
    try:
        return int(int_str)
    except ValueError:
        return None


def compare_not_none(f, a1, a2):
    if a1 is None and a2 is None: return None
    if a1 is None: return a2
    if a2 is None: return a1
    return f(a1, a2)


def can_user_write_group(system_user, group):
    if not system_user.is_authenticated: return False
    from app.init_model import role_master_name, role_teacher_name
    if system_user.system_role.name == role_master_name: return True
    if system_user.system_role.name == role_teacher_name:
        if system_user.teacher.id == group.teacher_id:
            return True
    return False


def notification_types_list_to_int(nt_list):
    result = 0
    for i in nt_list:
        if i >= 0:
            result += 1 << i
    return result


def notification_types_int_to_list(nt_int):
    result = []
    from app.models import notification_types_list
    for i in range(0, len(notification_types_list)):
        if nt_int & (1 << i) != 0:
            result.append(i)
    return result


days_of_week_names = ['пн', 'вт', 'ср', 'чт', 'пт', 'сб', 'вс']
