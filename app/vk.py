from threading import Thread

import requests


def send_vk_messages(subject, body, domains):
    def send_vk_messages_async():
        from app_holder import app_instance
        for domain in domains:
            r = requests.get('https://api.vk.com/method/messages.send',
                             {'v': '5.76', 'domain': domain, 'message': '{}\n{}'.format(subject, body),
                              'access_token': app_instance.config['VK_ACCESS_TOKEN']})
            print('send_vk_messages', r.json())

    thread = Thread(target=send_vk_messages_async)
    thread.start()
    return thread


def send_test_vk_message():
    send_vk_messages('test subject', body='text body', domains=['qwert2603', 'id201601008'])

# from app.vk import send_test_vk_message
