import datetime


def generate_login(last_name, first_name, second_name):
    login = ''
    login += translit(first_name[0])
    if len(second_name) > 0:
        login += translit(second_name[0])
    for c in last_name:
        login += translit(c)
    return login


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
start_month_teaching = 8  # September
end_month_teaching = 4  # May


def number_of_month(date):
    return (date.year - earliest_year) * months_per_year + date.month - 1


month_names = [
    'январь',
    'ферваль',
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
