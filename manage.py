#!./venv/bin/python3

import os
from flask_migrate import Migrate
from app import create_app, db
import app.models as models

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, SystemRole=models.SystemRole, SystemUser=models.SystemUser, Student=models.Student,
                Group=models.Group, StudentInGroup=models.StudentInGroup, Parent=models.Parent, Payment=models.Payment,
                Master=models.Master, Teacher=models.Teacher, Lesson=models.Lesson, Attending=models.Attending,
                Candidate=models.Candidate, DayPreference=models.DayPreference,
                SectionPreference=models.SectionPreference, ParentOfStudent=models.ParentOfStudent,
                Citizenship=models.Citizenship, School=models.School, Section=models.Section)


if __name__ == '__main__':
    app.run(
        # host='0.0.0.0',
        port=1918
    )
