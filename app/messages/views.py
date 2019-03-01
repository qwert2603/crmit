from flask import render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import or_

from app import db
from app.decorators import check_master_or_teacher_or_student
from app.init_model import role_master_name, role_teacher_name, role_student_name
from app.messages import messages
from app.messages.forms import SendMessageForm
from app.messages.utils import get_dialogs
from app.models import Message, SystemUser, SystemRole, MessageDetails


@messages.route("/dialogs_list")
@login_required
@check_master_or_teacher_or_student
def dialogs_list():
    page = request.args.get('page', 1, type=int)

    per_page = 20

    dialogs = get_dialogs(current_user.id, per_page * (page - 1), per_page)

    pagination = db.session.query(Message.receiver_id).filter(Message.sender_id == current_user.id).distinct()
    pagination = pagination.paginate(page, per_page=per_page, error_out=False)

    available_receivers = SystemUser.query \
        .join(SystemRole, SystemRole.id == SystemUser.system_role_id) \
        .filter(or_(SystemRole.name == role_master_name, SystemRole.name == role_teacher_name,
                    SystemRole.name == role_student_name)) \
        .all()

    return render_template('messages/dialogs_list.html', pagination=pagination, dialogs=dialogs,
                           available_receivers=available_receivers)


@messages.route("/messages_list/forward")
@login_required
@check_master_or_teacher_or_student
def messages_forward():
    receiver_id = request.args.get('receiver_id', 0, type=int)
    if receiver_id != 0: return redirect(url_for(".messages_list", receiver_id=receiver_id))
    return redirect(url_for(".dialogs_list"))


@messages.route("/messages_list/<int:receiver_id>", methods=['GET', 'POST'])
@login_required
@check_master_or_teacher_or_student
def messages_list(receiver_id):
    receiver = SystemUser.query.get_or_404(receiver_id)

    # todo: don't send messages from / to bots and developers.

    form = SendMessageForm()
    if form.validate_on_submit():
        message_details = MessageDetails(body=form.body.data)
        message_forward = Message(sender_id=current_user.id, receiver_id=receiver_id, message_details=message_details,
                                  forward=True)
        message_backward = Message(sender_id=receiver_id, receiver_id=current_user.id, message_details=message_details,
                                   forward=False)
        db.session.add(message_details)
        db.session.add(message_forward)
        db.session.add(message_backward)
        flash('сообщение отправлено')
        return redirect(url_for('.messages_list', receiver_id=receiver_id))

    page = request.args.get('page', 1, type=int)

    pagination = current_user.messages() \
        .filter(Message.receiver_id == receiver_id) \
        .join(MessageDetails, MessageDetails.id == Message.message_details_id) \
        .order_by(MessageDetails.send_time.desc())

    pagination = pagination.paginate(page, per_page=20, error_out=False)

    messages_items = pagination.items

    rendered = render_template('messages/messages_list.html', receiver=receiver, pagination=pagination,
                               messages=messages_items, form=form)

    for message in messages_items:
        if not message.forward:
            message.message_details.unread = False

    return rendered
