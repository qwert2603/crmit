#!./venv/bin/python3

from app import create_app
from wsgiref.handlers import CGIHandler
import os

os.environ['SCRIPT_NAME'] = ''

CGIHandler().run(create_app('prod'))