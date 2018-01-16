from flask import render_template, request, url_for, redirect, flash
from flask_login import login_required
from app.decorators import check_master_or_teacher
from app.models import Group, Student, StudentInGroup
from app.structure import structure
from app import db


@structure.route('/students_in_group/<int:id>', methods=['GET', 'POST'])
@login_required
@check_master_or_teacher
def students_in_group(id):
    group = Group.query.get_or_404(id)
    students_in_group = group.students_in_groups.all()
    in_group_students_ids = [s.student.id for s in students_in_group]
    if 'submit' in request.form:
        form_in_group = [int(i) for i in request.form.getlist('in_group')]
        print(in_group_students_ids)
        print(form_in_group)
        for new_id in form_in_group:
            if new_id not in in_group_students_ids:
                db.session.add(StudentInGroup(student_id=new_id, group_id=id))
        for old_student_in_group in students_in_group:
            if old_student_in_group.student.id not in form_in_group:
                if old_student_in_group.attendings_was.count() > 0:
                    flash('нельзя удалить {} из группы {}, так как он посещал занятия!'.format(
                        old_student_in_group.student.fio,
                        group.name))
                elif old_student_in_group.payments.count() > 0:
                    flash('нельзя удалить {} из группы {}, так как он вносил оплату!'.format(
                        old_student_in_group.student.fio,
                        group.name))
                else:
                    db.session.delete(old_student_in_group)
        flash('список учеников в группе {} изменен.'.format(group.name))
        return redirect(url_for('structure.groups_list'))
    other_students = Student.query \
        .filter(Student.id.notin_(in_group_students_ids)) \
        .order_by(Student.fio).all()
    return render_template('structure/students_in_group.html', group=group, students_in_group=students_in_group,
                           other_students=other_students)
