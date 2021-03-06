from flask import render_template, request, flash, redirect, url_for, abort
from flask_login import login_required, current_user
from sqlalchemy import or_

from app import db
from app.decorators import check_master_or_teacher, check_access_group_write
from app.init_model import role_master_name, role_teacher_name
from app.models import Notification, SystemUser, Group, receiver_type_group, receiver_type_student_in_group, SystemRole
from app.notifications import notifications
from app.notifications.forms import SendNotificationForm
from app.notifications.utils import parents_of_student_in_group, parents_of_group, do_send_notification


@notifications.route("/list")
@login_required
@check_master_or_teacher
def notifications_list():
    sender_id = request.args.get('sender_id', 0, type=int)
    page = request.args.get('page', 1, type=int)

    pagination = Notification.query.order_by(Notification.send_time.desc())
    if current_user.is_master:
        if sender_id > 0:
            pagination = pagination.filter(Notification.sender_id == sender_id)
    else:
        pagination = pagination.filter(Notification.sender_id == current_user.id)
    pagination = pagination.paginate(page, per_page=20, error_out=False)

    senders = SystemUser.query \
        .join(SystemRole, SystemRole.id == SystemUser.system_role_id) \
        .filter(or_(SystemRole.name == role_master_name, SystemRole.name == role_teacher_name)) \
        .all()

    if current_user.is_master:
        groups = Group.query
    else:
        groups = current_user.teacher.groups
    groups = groups.order_by(Group.start_month.desc(), Group.name).all()

    return render_template('notifications/notifications_list.html', sender_id=sender_id, pagination=pagination,
                           notifications=pagination.items, senders=senders, groups=groups)


@notifications.route("/send", methods=['GET', 'POST'])
@login_required
@check_access_group_write()
def send_notification():
    group_id = request.args.get('group_id', 0, type=int)
    group = Group.query.get_or_404(group_id)
    form = SendNotificationForm(group)
    if form.validate_on_submit():
        if current_user.is_developer: abort(403)
        subject = form.subject.data
        body = form.body.data
        receiver_id = form.receiver.data
        if receiver_id == 0:
            receiver_id = group_id
            receiver_type = receiver_type_group
            parents = parents_of_group(receiver_id)
        else:
            receiver_type = receiver_type_student_in_group
            parents = parents_of_student_in_group(receiver_id)
        receivers = do_send_notification(parents, subject, body)
        is_ok = True  # if receivers is not None:
        if is_ok:
            db.session.add(Notification(sender_id=current_user.id, receiver_type=receiver_type, receiver_id=receiver_id,
                                        subject=subject, body=body, receivers=receivers or ''))
            flash('уведомление отправлено!')
        else:
            flash('уведомление не отправлено, так как у родителей не выбраны типы уведомлений!')
        return redirect(url_for('.notifications_list'))
    return render_template('notifications/send.html', group=group, form=form)
