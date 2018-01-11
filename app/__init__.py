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
    return SystemUser.query.get(int(user_id))


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

    return app
