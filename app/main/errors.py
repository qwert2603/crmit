from flask import render_template

from . import main


@main.app_errorhandler(404)
def error404(e):
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def error500(e):
    return render_template('500.html'), 500


@main.app_errorhandler(403)
def error403(e):
    return render_template('403.html'), 403


@main.app_errorhandler(409)
def error409(e):
    return render_template('409.html'), 409
