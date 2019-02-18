from flask_mail import Message


def send_email(subject, body, recipients):
    msg = Message(subject, recipients=recipients)
    msg.body = body

    # def send_email_async():

    send = False
    if send:
        from app_holder import app_instance, mail_instance
        with app_instance.app_context():
            mail_instance.send(msg)


# thread = Thread(target=send_email_async)
# thread.start()
# return thread


def send_test_email():
    send_email('test subject', body='text body', recipients=['qwert2603@mail.ru', 'we_are_not_brothers@mail.ru'])

# from app.mail import send_test_email
