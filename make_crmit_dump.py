# 0 * * * * python3 /home/alex/crmit_dump/make_crmit_dump.py

import urllib.request
import datetime
import os
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate

base_dir = '/home/alex/crmit_dump'
dumps_dir = '{}/dumps'.format(base_dir)
os.makedirs(dumps_dir, exist_ok=True)
now_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
filename = '{}/{}.json'.format(dumps_dir, now_string)
write_file = open(filename, 'w')

credentials_file = open('{}/credentials.txt'.format(base_dir), 'r')
lines = credentials_file.read().splitlines()
access_token = lines[1]
mail_user = lines[3]
mail_password = lines[5]
credentials_file.close()


def send_email(subject, text):
    try:
        mail_receivers = ['qwert2603@mail.ru']

        msg = MIMEMultipart()
        msg['From'] = mail_user
        msg['To'] = COMMASPACE.join(mail_receivers)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject
        msg.attach(MIMEText(text))

        with open(filename, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=basename(filename)
            )
        part['Content-Disposition'] = 'attachment; filename="{}"'.format(basename(filename))
        msg.attach(part)

        server = smtplib.SMTP_SSL('smtp.mail.ru', 465)
        server.ehlo()
        server.login(mail_user, mail_password)
        server.sendmail(mail_user, mail_receivers, msg.as_string())
        server.close()
        return True
    except Exception as e:
        write_file.write(str(e))
        print(e)
        email_error_file = open(filename + '_email_error', 'w')
        email_error_file.write(str(e))
        email_error_file.close()
        return False


try:
    url = 'http://crm.cmit22.ru/api/v1.0.1/dump?access_token={}'.format(access_token)
    response = urllib.request.urlopen(url)
    response_string = response.read().decode("utf-8")
    write_file.write(response_string)

    b = send_email('crmit dump success', 'dump of {}'.format(now_string))
    if b: print('ok')
except Exception as e:
    write_file.write(str(e))
    write_file.close()
    send_email('crmit dump error', 'failed dump of {}'.format(now_string))
    print('not ok')
    print(e)
write_file.close()
