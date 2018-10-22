# 0 * * * * python3 /home/alex/crmit_dump/make_crmit_dump.py

import urllib.request
import datetime
import os

base_dir = '/home/alex/crmit_dump'
dumps_dir = '{}/dumps'.format(base_dir)
os.makedirs(dumps_dir, exist_ok=True)
now_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
filename = '{}/{}.json'.format(dumps_dir, now_string)
write_file = open(filename, 'w')
try:
    token_file = open('{}/access_token.txt'.format(base_dir), 'r')
    access_token = token_file.read()
    token_file.close()
    url = 'http://crm.cmit22.ru/api/v1.0.1/dump?access_token={}'.format(access_token)
    response = urllib.request.urlopen(url)
    response_string = response.read().decode("utf-8")
    write_file.write(response_string)
    print('ok')
except Exception as e:
    write_file.write(str(e))
    print('not ok')
write_file.close()
