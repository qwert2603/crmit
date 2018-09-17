from flask import render_template

from . import main


@main.app_errorhandler(404)
def error404(e):
    return render_template('error.html', message="404 - не найдено"), 404


@main.app_errorhandler(500)
def error500(e):
    return render_template('error.html', message="500 - внутренняя ошибка сервера"), 500


@main.app_errorhandler(403)
def error403(e):
    return render_template('error.html', message="403 - доступ запрещён"), 403


@main.app_errorhandler(409)
def error409(e):
    return render_template('error.html', message="409 - конфликт"), 409


@main.app_errorhandler(400)
def error400(e):
    return render_template('error.html', message="400 - ошибочный запрос"), 400
