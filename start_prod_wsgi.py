#!./venv/bin/python3

import os
from wsgiref.simple_server import make_server

from flask_mail import Mail

import app_holder
from app import create_app

os.environ['SCRIPT_NAME'] = ''

app = create_app('prod')
mail = Mail(app)

app_holder.mail_instance = mail


@app.context_processor
def context_processor():
    from start_dev import context_dict
    return context_dict


app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True

httpd = make_server('', 1918, app)
httpd.serve_forever()
