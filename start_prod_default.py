#!./venv/bin/python3

from flask_mail import Mail
import app_holder
from app import create_app, create_redirect_app
from wsgiref.handlers import CGIHandler
import os

os.environ['SCRIPT_NAME'] = ''

app = create_app('prod')
mail = Mail(app)

app_holder.mail_instance = mail


@app.context_processor
def context_processor():
    from start_dev import context_dict
    return context_dict


use_redirect = False
if use_redirect:
    CGIHandler().run(create_redirect_app())
else:
    CGIHandler().run(app)
