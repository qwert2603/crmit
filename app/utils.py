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
