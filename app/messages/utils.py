from app import db


class Dialog:
    def __init__(self, receiver_id, unread_count):
        self.receiver_id = receiver_id
        self.unread_count = unread_count


def get_dialogs(owner_id, offset, limit):
    sql = '''
        select r.receiver_id,
               count(message_details.unread)        as unread_count,
               max(message_details_times.send_time) as last_message_time
        from (select distinct id, receiver_id, message_details_id from messages where messages.owner_id = {}) r
               left join (select * from messages where messages.forward = false) messages
                         on messages.id = r.id
               left join (select * from message_details where message_details.unread = true) message_details
                         on messages.message_details_id = message_details.id
               left join (select * from message_details) message_details_times
                         on r.message_details_id = message_details_times.id
        group by r.receiver_id
        order by last_message_time desc
        offset {} limit {}
    '''.format(owner_id, offset, limit)

    rows = db.engine.execute(sql)
    result = []
    for row in rows:
        result.append(Dialog(row[0], row[1]))
    return result
