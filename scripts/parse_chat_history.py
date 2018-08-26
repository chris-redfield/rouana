#!/usr/bin/env python3

import argparse
import json
import logging
import requests
import os
import time
from rocketchat import RocketChatBot

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
channels_ids = []

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
        logger.info('>> Creating folder {}'.format(path))
    else:
        logger.info('>> Directory {} already exists'.format(path))

def create_file(path, file_name):
    logger.info(">> Creating file {}".format(path + file_name))
    file = open(path + file_name, 'w+')
    return file

def create_bot():
    bot = RocketChatBot(user_name,user_password,server='localhost:3000',ssl=False)
    return bot

def process_channel_messages(conversation_id, conversation_messages):
    #for el in conversation_messages:
        #print("foi \n\n", str(el['ts'])[:10],"\n\n")
        #if 'name' in el['u']:
        #    user_name = el['u']['name']
        #else:
        #    user_name = el['u']['username']
    #    print(str(el['ts'])[:10])

    path = 'messages/' + str(conversation_id) + '/'
    create_folder(path)
    file_name = str(conversation_messages[0]['ts'])[:10] + '.txt'
    f = create_file(path, file_name)

    for message_data in reversed(conversation_messages):
        time = str(message_data['ts'])
        username = ""

        if 'name' in message_data['u'] and message_data['u']['name'] != None:
            username = message_data['u']['name']
        else:
            username = message_data['u']['username']

        if username == None:
            print("Message data foi \n", message_data, "\n\n")

        message = message_data['msg']

        line = time + ' ' + username +': '+ message + '\n'

        if time[:10] != file_name[:10]:
            print("Entrou aki e time foi ",time[:10]," e file_name foi ",file_name[:10])
            f.close()
            f = create_file(path, time[:10] + '.txt')
            print("ENTROUUUU AKIII e line foi", line,"\n\n\n")

        f.write(line)

    f.close()

def get_channels_history(bot, message):
    for channel_id in channels_ids:
        logger.info('>> Get messages for channel {}'.format(channel_id))
        bot.getHistory(channel_id)

if __name__ == '__main__':
    logger.info('===== Automatic env configuration =====')

    user_header = get_authentication_token()
    bot = create_bot()
    bot.addPrefixHandler('get messages', get_channels_history)

    if user_header:
        create_folder('messages')
        logger.info('>> Get all rooms for user {}'.format(user_name))
        channels_ids = get_user_rooms()

        bot.start()        

        while True:
            if len(bot.conversations_messages) == len(channels_ids):
                break

        for conversation_id, conversation_messages in bot.conversations_messages.items():
            process_channel_messages(conversation_id, conversation_messages)
    else:
        logger.error('Login Failed')
