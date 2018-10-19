#!./venv/bin/python3

from app import create_app
from wsgiref.handlers import CGIHandler
import os

os.environ['SCRIPT_NAME'] = ''

app = create_app('prod')
mail = Mail(app)

app_holder.app_instance = app
app_holder.mail_instance = mail

@app.context_processor
def context_processor():
    from manage import context_dict
    return context_dict

CGIHandler().run(app)