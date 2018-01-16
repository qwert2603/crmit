from flask import render_template, request
from flask_login import login_required
from app.decorators import check_master_or_teacher
from app.models import Group, Student
from app.structure import structure


@structure.route('/students_in_group/<int:id>', methods=['GET', 'POST'])
@login_required
@check_master_or_teacher
def students_in_group(id):
    group = Group.query.get_or_404(id)
    print(request.form.getlist('in_group'))
    students_in_group = group.students_in_groups.all()
    in_group_students_ids = [s.student.id for s in students_in_group]
    other_students = Student.query \
        .filter(Student.id.notin_(in_group_students_ids)) \
        .order_by(Student.fio).all()
    return render_template('structure/students_in_group.html', group=group, students_in_group=students_in_group,
                           other_students=other_students)
