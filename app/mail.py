from threading import Thread

from flask_mail import Message


def send_email(subject, body, recipients):
    msg = Message(subject, recipients=recipients)
    msg.body = body

    def send_email_async():
        from manage import app, mail
        with app.app_context():
            mail.send(msg)

    thread = Thread(target=send_email_async)
    thread.start()
    return thread


def send_test_email():
    send_email('test subject', body='text body', recipients=['qwert2603@mail.ru', 'we_are_not_brothers@mail.ru'])

# from app.mail import send_test_email
