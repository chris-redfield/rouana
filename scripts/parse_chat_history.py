#!/usr/bin/env python3

import argparse
import json
import logging
import requests
import os

# == Log Config ==

logger = logging.getLogger('Parse Chats History')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter(
    '%(asctime)s :: %(name)s :: %(levelname)s :: %(message)s'
)

ch.setFormatter(formatter)

logger.addHandler(ch)

# == CLI ==

parser = argparse.ArgumentParser()

parser.add_argument(
    '--user-name', '-un', type=str, default='rouana',
    help='Admin username (default: rouana)'
)
parser.add_argument(
    '--user-password', '-up', type=str, default='rouana',
    help='Admin password (default: rouana)'
)
parser.add_argument(
    '--rocketchat-url', '-r', type=str, default='http://localhost:3000',
    help='Rocket chat URL (default: http://localhost:3000)'
)

args = parser.parse_args()


host = args.rocketchat_url
if host[-1] == '/':
    host = host[:-1]

login_path = '/api/v1/login'

user_name = args.user_name
user_password = args.user_password
user_header = None

def get_authentication_token():
    login_data = {'username': user_name, 'password': user_password}
    response = requests.post(host + login_path, data=json.dumps(login_data))

    if response.json()['status'] == 'success':
        logger.info('Login suceeded')

        authToken = response.json()['data']['authToken']
        userId = response.json()['data']['userId']
        user_header = {
            'X-Auth-Token': authToken,
            'X-User-Id': userId,
            'Content-Type': 'application/json'
        }

        return user_header

def get_user_rooms():
    get_rooms_response = requests.get(
        host + '/api/v1/rooms.get',
        headers = user_header
    )

    channels_ids = []
    rooms_data = get_rooms_response.json()['update']

    for channel_data in rooms_data:
        channels_ids.append(channel_data['_id'])

    return channels_ids

def create_folder(folder_name):
    path = './' + str(folder_name)
    if not os.path.isdir(path):
        os.mkdir(path)
        logger.info('Creating folder {}'.format(path))
    else:
        logger.info('Directory {} already exists'.format(path))

def get_channel_history(channel_id):
    get_history_response = requests.get(
        host + '/api/v1/im.history?roomId=' + channel_id,
        headers = user_header
    )
    if get_history_response.json()['success']:
        messages_data = get_history_response.json()['messages']
        path = 'messages/' + str(channel_id) + '/'
        create_folder(path)
        file_name = messages_data[0]['ts'][:10] + '.txt'
        f = open(path + file_name, 'w+')
        for message_data in reversed(messages_data):
            time = message_data['ts']
            username = message_data['u']['username']
            message = message_data['msg']
            line = time + ' ' + username +': '+ message + '\n'
            f.write(line)
            print(line)

        f.close()
    else:
        logger.error('>> Cannot get the messages of this channel')

if __name__ == '__main__':
    logger.info('===== Automatic env configuration =====')

    user_header = get_authentication_token()

    if user_header:
        create_folder('messages')
        logger.info('>> Get all rooms for user {}'.format(user_name))
        channels_ids = get_user_rooms()

        for channel_id in channels_ids:
            logger.info('>> Get messages for channel {}'.format(channel_id))
            get_channel_history(channel_id)

    else:
        logger.error('Login Failed')
