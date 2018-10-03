from app.main import main
from flask import render_template


@main.route('/')
def index():
    return render_template('index.html', hide_who_u_r=True)
