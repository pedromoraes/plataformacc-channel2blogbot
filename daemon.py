import argparse
import time
import telepot
import os
from pprint import pprint
from telepot.loop import MessageLoop
from create_blog_post import create_blog_post
from get_photo import get_photo
from format_message import format_message

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--dev', dest='devmode', action='store_true')
    parser.add_argument('-v', dest='verbose', action='store_true')
    args = parser.parse_args()

    pprint(args)

    if args.devmode:
        botkey = os.environ['TELEBOT_KEY_DEV']
    else:
        botkey = os.environ['TELEBOT_KEY']

    bot = telepot.Bot(botkey)
    pprint(bot.getMe())

    last_id = 0

    def handle_user(user_updates):
        by_date = {}
        is_edit = False
        for m in user_updates:
            if not m['date'] in by_date:
                by_date[m['date']] = []

            for prev in by_date[m['date']].copy():
                if prev['message_id'] == m['message_id']:
                    by_date[m['date']].remove(prev)
            by_date[m['date']].append(m)

        for date in by_date:
            last = by_date[date][-1]
            create_blog_post({
                'photo': list(filter(None, map(lambda x: get_photo(bot, x), by_date[date]))),
                'caption': last['caption'] if 'caption' in last else '',
                'text': format_message(by_date[date]),
                'message_id': [m['message_id'] for m in by_date[date]],
                'username': last['chat']['username'],
                'edit': is_edit
            })

    while 1:
        updates = bot.getUpdates()
        users = {}
        for update in updates:
            if update['update_id'] <= last_id:
                continue
            last_id = update['update_id']

            if args.devmode: pprint(update)

            if 'channel_post' in update:
                m = update['channel_post']
            elif 'edited_channel_post' in update:
                m = update['edited_channel_post']
                is_edit = True
            else:
                print('unknown update')
                pprint(update)
                continue

            user = m['chat']['username']
            if not user in users: users[user] = []
            users[user].append(m)

        for user in users:
            handle_user(users[user])

        time.sleep(10)
