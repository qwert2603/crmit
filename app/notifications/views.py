from flask import render_template, request, flash, redirect, url_for
from flask_login import login_required, current_user
from sqlalchemy import or_

from app import db
from app.decorators import check_master_or_teacher, check_access_group_write
from app.init_model import role_master_name
from app.mail import send_email
from app.models import Notification, SystemUser, Group, receiver_type_group, receiver_type_student_in_group, \
    StudentInGroup
from app.notifications import notifications
from app.notifications.forms import SendNotificationForm


@notifications.route("/list")
@login_required
@check_master_or_teacher
def notifications_list():
    sender_id = request.args.get('sender_id', 0, type=int)
    page = request.args.get('page', 1, type=int)
    pagination = Notification.query.order_by(Notification.send_time.desc())
    if sender_id > 0: pagination = pagination.filter(Notification.sender_id == sender_id)
    pagination = pagination.paginate(page, per_page=20, error_out=False)
    senders = SystemUser.query \
        .filter(or_(SystemUser.system_role_id == 1, SystemUser.system_role_id == 2)) \
        .all()
    if current_user.system_role.name == role_master_name:
        groups = Group.query.all()
    else:
        groups = current_user.teacher.groups.all()
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
        subject = form.subject.data
        body = form.body.data
        receiver_id = form.receiver.data
        if receiver_id == 0:
            receiver_id = group_id
            receiver_type = receiver_type_group
            parents = []
            for student in group.students:
                for parent in student.parents:
                    parents.append(parent)
        else:
            receiver_type = receiver_type_student_in_group
            parents = StudentInGroup.query.get_or_404(receiver_id).student.parents.all()
        recipients = []
        for parent in parents:
            if parent.email is not None:
                recipients.append(parent.email)
        if len(recipients) > 0:
            send_email(subject, body, recipients)
            db.session.add(Notification(sender_id=current_user.id, receiver_type=receiver_type, receiver_id=receiver_id,
                                        subject=subject, body=body, receivers='\n'.join(recipients)))
            flash('уведомление отправлено!')
        else:
            flash('уведомление не отправлено, так как у родителей не указана почта!')
        return redirect(url_for('.notifications_list'))
    return render_template('notifications/send.html', group=group, form=form)
