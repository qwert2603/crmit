import os

basedir = os.path.abspath(os.path.dirname(__file__))

DB_TYPE_POSTGRES = 'postgres'
DB_TYPE_MYSQL = 'mysql'


class Config:
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass


class DevConfig(Config):
    DEBUG = True
    SECRET_KEY = '1918'
    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db_dev.sqlite')
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:1234@127.0.0.1:5432/crmit'
    DB_TYPE = DB_TYPE_POSTGRES
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'natalykanatkina'
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = 'natalykanatkina@gmail.com'
    VK_ACCESS_TOKEN = os.getenv('VK_ACCESS_TOKEN')
    ACCESS_TOKEN_SALT = '1918'.encode('utf-8')


class ProdConfig(Config):
    SECRET_KEY = '<key>'  # todo
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://kristallp_crm:<psw>@kristallp.mysql/kristallp_crm'  # todo
    DB_TYPE = DB_TYPE_MYSQL
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = 'natalykanatkina'
    MAIL_PASSWORD = '<pws>'  # todo
    MAIL_DEFAULT_SENDER = 'natalykanatkina@gmail.com'
    VK_ACCESS_TOKEN = '<token>'  # todo
    ACCESS_TOKEN_SALT = '<salt>'.encode('utf-8')  # todo


config = {
    'dev': DevConfig,
    'prod': ProdConfig,

    'default': DevConfig
}
