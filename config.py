import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = '1918'  # todo
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass


class DevConfig(Config):
    DEBUG = True
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db_dev.sqlite')
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:1234@192.168.1.26:5432/crmit'


class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://kristallp_crm:<psw>@kristallp.mysql/kristallp_crm'  # todo


config = {
    'dev': DevConfig,
    'prod': ProdConfig,

    'default': DevConfig
}
