from app.main import main
from flask import render_template


@main.route('/')
def index():
    return render_template('base.html')


@main.route('/users')
def users():
    return render_template('base.html')
