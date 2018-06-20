from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config

bootstrap = Bootstrap()
moment = Moment()
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'users.login'

from app.models import AnonUser, SystemUser

login_manager.anonymous_user = AnonUser


@login_manager.user_loader
def load_user(user_id):
    system_user = SystemUser.query.get(int(user_id))
    if system_user is not None and system_user.enabled: return system_user


def create_app(config_name):
    app = Flask(__name__)
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

    return app
