from flask_login import login_required

from app.decorators import check_master
from app.main import main
from flask import render_template, jsonify

from app.main.dump_utils import db_to_dump


@main.route('/')
def index():
    return render_template('index.html', hide_who_u_r=True)


@main.route('/anth')
@login_required
@check_master
def anth():
    return render_template('anth.html')


@main.route('/dump')
@login_required
@check_master
def dump():
    return jsonify(db_to_dump())
