#!./venv/bin/python3

from app import create_app
from wsgiref.handlers import CGIHandler
import os

os.environ['SCRIPT_NAME'] = ''

app = create_app('prod')

from app.init_model import role_master_name, role_teacher_name, role_student_name

@app.context_processor
def context_processor():
    return dict(role_master_name=role_master_name, role_teacher_name=role_teacher_name,
                role_student_name=role_student_name)

CGIHandler().run(app)