from flask import Flask, request, redirect
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy

import app_holder
from config import config

bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'users.login'

from app.models import AnonUser, SystemUser, PageVisit

login_manager.anonymous_user = AnonUser


@login_manager.user_loader
def load_user(user_id):
    system_user = SystemUser.query.get(int(user_id))
    if system_user is not None and system_user.is_bot: return None
    if system_user is not None and system_user.enabled and not system_user.force_ask_to_login: return system_user


def create_redirect_app():
    app = Flask(__name__)

    redirect_url = 'http://crm.cmit22.ru:1918'

    @app.route('/')
    def main():
        return redirect(redirect_url)

    @app.errorhandler(404)
    def error404(e):
        return redirect(redirect_url)

    return app


def create_app(config_name):
    app = Flask(__name__)
    app_holder.app_instance = app
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)

    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.users import users as users_blueprint
    app.register_blueprint(users_blueprint, url_prefix='/users')

    from app.structure import structure as structure_blueprint
    app.register_blueprint(structure_blueprint, url_prefix='/structure')

    from app.lessons import lessons as lessons_blueprint
    app.register_blueprint(lessons_blueprint, url_prefix='/lessons')

    from app.stat import stat as stat_blueprint
    app.register_blueprint(stat_blueprint, url_prefix='/stat')

    from app.payments import payments as payments_blueprint
    app.register_blueprint(payments_blueprint, url_prefix='/payments')

    from app.notifications import notifications as notifications_blueprint
    app.register_blueprint(notifications_blueprint, url_prefix='/notifications')

    from app.schedule import schedule as schedule_blueprint
    app.register_blueprint(schedule_blueprint, url_prefix='/schedule')

    from app.student import student as student_blueprint
    app.register_blueprint(student_blueprint, url_prefix='/student')

    from app.messages import messages as messages_blueprint
    app.register_blueprint(messages_blueprint, url_prefix='/messages')

    from app.api_1_0_1 import api_1_0_1 as api_1_0_1_blueprint
    app.register_blueprint(api_1_0_1_blueprint, url_prefix='/api/v1.0.1')

    @app.after_request
    def after_request(response):
        endpoint = request.endpoint
        if endpoint is None: return response

        page_visit = PageVisit.query.filter(PageVisit.page_name == endpoint).first()
        if page_visit is not None:
            page_visit.visits_count = page_visit.visits_count + 1
        else:
            db.session.add(PageVisit(page_name=endpoint, visits_count=1))
        return response

    return app
