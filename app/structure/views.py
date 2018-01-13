from flask import render_template, request
from flask_login import login_required
from app.decorators import check_master_or_teacher
from app.structure import structure
from app.models import Group


@structure.route('/students_in_group/<int:id>', methods=['GET', 'POST'])
@login_required
@check_master_or_teacher
def students_in_group(id):
    group = Group.query.get_or_404(id)
    print(request.form.getlist('in_group'))
    students = [
        {'id': 1, 'fio': 'Alex'},
        {'id': 2, 'fio': 'Elena'},
        {'id': 3, 'fio': 'Nikita'}
    ]
    others = [{'id': 10, 'fio': 'Anna'}]
    return render_template('structure/students_in_group.html', group=group, students=students, others=others)
