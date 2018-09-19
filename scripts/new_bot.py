import time
import json
import requests
from rocketchat_py_sdk.driver import Driver

bot_username = 'rouana'
bot_password = 'rouana'
rocket_url = 'localhost:3000'

def is_bot_logged():
    data = requests.get(rocket_url + '/api/v1/rooms.get')
    print('='*50)
    print(data)
    print('='*50)

def start(bot):
    bot.connect()
    bot.login(user=bot_username, password=bot_password)

    bot.subscribe_to_messages()
    #is_bot_logged()
    while True:
        time.sleep(3600)

 
if __name__ == '__main__':
    start(Driver(url=rocket_url, ssl=False, debug=True))
    
