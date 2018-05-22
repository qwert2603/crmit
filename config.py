import os

basedir = os.path.abspath(os.path.dirname(__file__))

DB_TYPE_POSTGRES = 'postgres'
DB_TYPE_MYSQL = 'mysql'
DB_TYPE = DB_TYPE_POSTGRES


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
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'natalykanatkina'
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = 'natalykanatkina@gmail.com'
    VK_ACCESS_TOKEN = os.getenv('VK_ACCESS_TOKEN')


# todo: all prod psws to separate file.
class ProdConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://kristallp_crm:<psw>@kristallp.mysql/kristallp_crm'  # todo
    # todo: prod mail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'natalykanatkina'
    MAIL_PASSWORD = '<pws>'
    MAIL_DEFAULT_SENDER = 'natalykanatkina@gmail.com'
    VK_ACCESS_TOKEN = '<token>'  # todo


config = {
    'dev': DevConfig,
    'prod': ProdConfig,

    'default': DevConfig
}
