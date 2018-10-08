from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from app import db
from app.decorators import check_master_or_teacher
from app.init_model import role_master_name
from app.models import Group, ScheduleTime, ScheduleGroup
from app.schedule import schedule
from app.utils import days_of_week_names


@schedule.route('/', methods=['GET', 'POST'])
@login_required
@check_master_or_teacher
def timetable():
    schedule_groups = dict()
    for sg in ScheduleGroup.query.all():
        if sg.schedule_time.id not in schedule_groups:
            schedule_groups[sg.schedule_time.id] = dict()
        schedule_groups[sg.schedule_time.id][sg.day_of_week] = sg

    is_master = current_user.system_role.name == role_master_name

    if 'submit' in request.form:
        if not is_master:
            flash('вы не можете редактировать расписание.')
            return redirect(url_for('.timetable'))
        schedule_times = ScheduleTime.query.order_by(ScheduleTime.id).all()
        for schedule_time in schedule_times:
            new_time = request.form.get('time_{}'.format(schedule_time.id), '')
            if new_time == '': new_time = None
            schedule_time.time = new_time
            for day_of_week_index in range(0, len(days_of_week_names)):
                new_group_id = request.form.get('group_{}_{}'.format(schedule_time.id, day_of_week_index), 0, type=int)
                if new_group_id == 0: new_group_id = None
                schedule_group = schedule_groups.get(schedule_time.id, dict()).get(day_of_week_index)
                if schedule_group is None:
                    db.session.add(ScheduleGroup(schedule_time=schedule_time,
                                                 day_of_week=day_of_week_index,
                                                 group_id=new_group_id))
                else:
                    schedule_group.group_id = new_group_id
        flash('расписание сохранено.')
        return redirect(url_for('.timetable'))

    return render_template('schedule/timetable_master.html' if is_master else 'schedule/timetable_teacher.html',
                           groups=Group.query.order_by(Group.name).all(),
                           days_of_week=days_of_week_names,
                           schedule_times=ScheduleTime.query.order_by(ScheduleTime.time, ScheduleTime.id).all(),
                           schedule_groups=schedule_groups)
