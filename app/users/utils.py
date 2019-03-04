from sqlalchemy import or_

from app import db
from app.models import Message, MessageDetails


def delete_all_messages_with_user(system_user_id):
    messages = Message.query \
        .filter(or_(Message.owner_id == system_user_id, Message.receiver_id == system_user_id)) \
        .all()
    messages_details = MessageDetails.query \
        .join(Message, Message.message_details_id == MessageDetails.id) \
        .filter(or_(Message.owner_id == system_user_id, Message.receiver_id == system_user_id)) \
        .all()

    for m in messages: db.session.delete(m)
    for md in messages_details: db.session.delete(md)
