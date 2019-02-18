import datetime

from flask import request, render_template, abort, flash, url_for, redirect
from flask_login import login_required, current_user

from app import db
from app.decorators import check_master_or_teacher, check_access_group_write, check_master
from app.is_removable_check import is_lesson_removable
from app.lessons import lessons
from app.lessons.utils import lessons_lists, dates_of_lessons_dict, empty_past_lessons, fill_group_by_schedule
from app.models import Lesson, Group, Payment, StudentInGroup, Attending, Teacher, Student, ScheduleGroup, \
    attending_was_not
from app.payments.utils import payments_in_month_dicts
from app.utils import get_month_name, parse_date_or_none, number_of_month_for_date, start_date_of_month, \
    end_date_of_month, can_user_write_group, days_of_week_names, parse_int_or_none, redirect_back_or_home


@lessons.route('/list')
@login_required
@check_master_or_teacher
def lessons_list():
    group_id = request.args.get('group_id', 0, type=int)
    teacher_id = request.args.get('teacher_id', 0, type=int)
    selected_date = parse_date_or_none(request.args.get('selected_date'))
    page = request.args.get('page', 1, type=int)
    pagination = Lesson.query.order_by(Lesson.date.desc())
    if group_id > 0: pagination = pagination.filter(Lesson.group_id == group_id)
    if teacher_id > 0: pagination = pagination.filter(Lesson.teacher_id == teacher_id)
    if selected_date is not None: pagination = pagination.filter(Lesson.date <= selected_date)
    pagination = pagination.paginate(page, per_page=20, error_out=False)
    return render_template('lessons/lessons_list.html', group_id=group_id, teacher_id=teacher_id,
                           selected_date=selected_date, pagination=pagination, lessons=pagination.items,
                           groups=Group.list_sorted_for_current_user().all(),
                           teachers=Teacher.query.order_by(Teacher.fio).all())


@lessons.route('/months/<int:group_id>')
@login_required
@check_master_or_teacher
def months_list(group_id):
    group = Group.query.get_or_404(group_id)
    dates_of_lessons = dates_of_lessons_dict(group_id)
    months = [{'month_number': month_number, 'month_name': get_month_name(month_number),
               'lessons_dates': dates_of_lessons.get(month_number)}
              for month_number in range(group.start_month, group.end_month + 1)]
    return render_template('lessons/months_list.html', group=group, months=months)


@lessons.route('/<int:group_id>/<int:month_number>', methods=['GET', 'POST'])
@login_required
@check_master_or_teacher
def lessons_in_month(group_id, month_number):
    group = Group.query.get_or_404(group_id)
    if month_number < group.start_month or month_number > group.end_month:
        abort(404)
    month_name = get_month_name(month_number)
    students_in_group = group.students_in_group_in_month(month_number) \
        .join(Student, Student.id == StudentInGroup.student_id) \
        .order_by(Student.fio) \
        .all()
    if 'submit' in request.form:
        if not can_user_write_group(current_user, group): abort(403)
        ls = Lesson.lessons_in_group_in_month(group_id, month_number).all()
        ps = Payment.query \
            .join(StudentInGroup, StudentInGroup.id == Payment.student_in_group_id) \
            .filter(StudentInGroup.group_id == group_id, Payment.month == month_number)
        payments = dict()
        for p in ps:
            payments[p.student_in_group_id] = p
        for student_in_group in students_in_group:
            new_value = request.form.get('p_{}'.format(student_in_group.id), 0, type=int)
            if new_value < 0: new_value = 0
            max_value = group.section.price - student_in_group.discount
            if new_value > max_value: new_value = max_value
            payment = payments.get(student_in_group.id)
            is_cash = 'c_{}'.format(student_in_group.id) in request.form
            comment = request.form.get('comment_{}'.format(student_in_group.id), '')
            if payment is not None:
                if not payment.confirmed:
                    payment.value = new_value
                    payment.cash = is_cash
                    payment.comment = comment
            else:
                db.session.add(Payment(student_in_group=student_in_group, month=month_number, value=new_value,
                                       cash=is_cash, comment=comment))
            attendings = dict()
            for l in ls:
                attendings[l.id] = dict()
                for a in l.attendings:
                    attendings[l.id][a.student_id] = a
            for l in ls:
                attending = attendings[l.id].get(student_in_group.student_id)
                a_key = 'a_{}_{}'.format(l.id, student_in_group.student_id)
                new_state = request.form.get(a_key, attending_was_not, type=int)
                if attending is not None:
                    attending.state = new_state
                else:
                    db.session.add(Attending(lesson=l, student=student_in_group.student, state=new_state))
        flash('посещения и оплата в группе {} за {} сохранены.'.format(group.name, month_name))
        return redirect(url_for('lessons.lessons_in_month', group_id=group_id, month_number=month_number))
    pd = payments_in_month_dicts(group_id, month_number)
    ll = lessons_lists(group_id, month_number)
    return render_template('lessons/lessons_in_month.html', group=group, month_number=month_number,
                           month_name=month_name, students_in_group=students_in_group, payments=pd[0], confirmed=pd[1],
                           cash=pd[2], comments=pd[3], lessons=ll[0], attendings_states=ll[1],
                           write_mode=can_user_write_group(current_user, group))


@lessons.route('/create/<int:group_id>', methods=['GET', 'POST'])
@login_required
@check_access_group_write()
def create_lesson(group_id):
    group = Group.query.get_or_404(group_id)
    if 'submit' in request.form:
        date = parse_date_or_none(request.form.get('date'))
        if date is None or date < start_date_of_month(group.start_month) or date > end_date_of_month(group.end_month):
            abort(409)
        if current_user.is_teacher and date < datetime.date.today():
            abort(409)
        db.session.add(Lesson(group_id=group_id, teacher_id=group.teacher_id, date=date))
        flash('занятие создано: {}'.format(date))
        return redirect(url_for('.lessons_in_month', group_id=group_id, month_number=number_of_month_for_date(date)))
    return render_template('lessons/create_lesson.html', group=group)


@lessons.route('/delete/<int:lesson_id>')
@login_required
@check_master_or_teacher
def delete_lesson(lesson_id):
    lesson = Lesson.query.get_or_404(lesson_id)
    # can't use @check_access_group_write() because no 'group_id' param.
    if not can_user_write_group(current_user, lesson.group): abort(403)
    if not is_lesson_removable(lesson): abort(409)
    if current_user.is_teacher and lesson.date < datetime.date.today(): abort(409)
    for a in lesson.attendings_was_not:
        db.session.delete(a)
    db.session.delete(lesson)
    flash('занятие {} в {} удалено'.format(lesson.date, lesson.group.name))
    return redirect_back_or_home()


@lessons.route('/delete_empty_past', methods=['GET', 'POST'])
@login_required
@check_master
def delete_empty_past_lessons():
    if 'submit' in request.form:
        count = 0
        for k in request.form:
            if k[:2] == 'l_':
                count += 1
                lesson_id = parse_int_or_none(k[2:])
                if lesson_id is None:
                    abort(409)
                lesson = Lesson.query.get(lesson_id)
                for a in lesson.attendings_was_not:
                    db.session.delete(a)
                db.session.delete(lesson)
        flash('удалено занятий: {}'.format(count))
        return redirect(url_for('.lessons_list'))
    return render_template('lessons/delete_empty_past.html', lessons=empty_past_lessons())


@lessons.route('/fill_by_schedule/<int:group_id>', methods=['GET', 'POST'])
@login_required
@check_access_group_write()
def fill_by_schedule(group_id):
    group = Group.query.get_or_404(group_id)
    if 'submit' in request.form:
        new_dows = []
        for k in request.form:
            if k[:4] == 'dow_':
                dow = parse_int_or_none(k[4:])
                if dow is None:
                    abort(409)
                new_dows.append(dow)
        fill_group_by_schedule(group, new_dows)
        flash('расписание сформировано')
        return redirect(url_for('.months_list', group_id=group_id))
    checked_days = db.session.query(ScheduleGroup.day_of_week) \
        .distinct() \
        .filter(ScheduleGroup.group_id == group_id) \
        .all()
    checked_days = [r[0] for r in checked_days]
    return render_template('lessons/fill_by_schedule.html', group=group, days_of_week_names=days_of_week_names,
                           checked_days=checked_days)
