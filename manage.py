#!./venv/bin/python3

import os
from flask_migrate import Migrate
from app import create_app, db
import app.models as models
from app.init_model import role_master_name, role_teacher_name, role_student_name
from app.is_removable_check import is_section_removable, is_group_removable, is_parent_removable, is_school_removable, \
    is_citizenship_removable, is_student_removable, is_master_removable, is_teacher_removable, is_lesson_removable
from app.utils import start_date_of_month, end_date_of_month, number_of_month_for_date, get_month_name, \
    can_user_write_group

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


context_dict = dict(role_master_name=role_master_name, role_teacher_name=role_teacher_name,
                    role_student_name=role_student_name, start_date_of_month=start_date_of_month,
                    end_date_of_month=end_date_of_month, number_of_month_for_date=number_of_month_for_date,
                    get_month_name=get_month_name, can_user_write_group=can_user_write_group,
                    is_section_removable=is_section_removable, is_group_removable=is_group_removable,
                    is_parent_removable=is_parent_removable, is_school_removable=is_school_removable,
                    is_citizenship_removable=is_citizenship_removable, is_master_removable=is_master_removable,
                    is_teacher_removable=is_teacher_removable, is_student_removable=is_student_removable,
                    is_lesson_removable=is_lesson_removable)


@app.context_processor
def context_processor():
    return context_dict


if __name__ == '__main__':
    app.run(
        # host='0.0.0.0',
        port=1918
    )
