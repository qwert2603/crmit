from flask import jsonify

from app.api_1_0 import api_1_0
from app.api_1_0.json_utils import section_to_json, teacher_to_json, master_to_json, student_to_json_brief, \
    student_to_json_full, group_to_json_full, group_to_json_brief, student_in_group_to_json, lesson_to_json, \
    attending_to_json
from app.api_1_0.utils import create_json_list, create_attendings_for_all_students
from app.init_model import developer_login
from app.models import Section, Teacher, Master, Student, SystemUser, Group, Lesson, Attending, StudentInGroup


@api_1_0.route('/sections_list')
def sections_list():
    return create_json_list(Section, Section.name, section_to_json)


@api_1_0.route('/groups_list')
def groups_list():
    return create_json_list(Group, Group.name, group_to_json_brief)


@api_1_0.route('/teachers_list')
def teachers_list():
    return create_json_list(Teacher, Teacher.fio, teacher_to_json)


@api_1_0.route('/masters_list')
def masters_list():
    return create_json_list(Master, Master.fio, master_to_json,
                            lambda query: query
                            .join(SystemUser, SystemUser.id == Master.system_user_id)
                            .filter(SystemUser.login != developer_login)
                            )


@api_1_0.route('/students_list')
def students_list():
    return create_json_list(Student, Student.fio, student_to_json_brief,
                            lambda query: query
                            .order_by(Student.filled, Student.id)
                            )


@api_1_0.route('student_details/<int:student_id>')
def student_details(student_id):
    return jsonify(student_to_json_full(Student.query.get_or_404(student_id)))


@api_1_0.route('group_details/<int:group_id>')
def group_details(group_id):
    return jsonify(group_to_json_full(Group.query.get_or_404(group_id)))


@api_1_0.route('section_details/<int:section_id>')
def section_details(section_id):
    return jsonify(section_to_json(Section.query.get_or_404(section_id)))


@api_1_0.route('teacher_details/<int:teacher_id>')
def teacher_details(teacher_id):
    return jsonify(teacher_to_json(Teacher.query.get_or_404(teacher_id)))


@api_1_0.route('students_in_group/<int:group_id>')
def students_in_group(group_id):
    group = Group.query.get_or_404(group_id)
    students_in_group_list = group.students_in_group.order_by(StudentInGroup.id)
    return jsonify([student_in_group_to_json(student_in_group) for student_in_group in students_in_group_list])


@api_1_0.route('lessons_in_group/<int:group_id>')
def lessons_in_group(group_id):
    group = Group.query.get_or_404(group_id)
    return jsonify([lesson_to_json(lesson) for lesson in group.lessons.order_by(Lesson.date.desc())])


@api_1_0.route('attendings_of_lesson/<int:lesson_id>')
def attendings_of_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    create_attendings_for_all_students(lesson)
    return jsonify([attending_to_json(attending) for attending in lesson.attendings.order_by(Attending.id)])
