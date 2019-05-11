import os

def get_photo(bot, msg):
    if 'photo' in msg:
        if not os.path.isdir('tmp'): os.makedirs('tmp')
        id = msg['photo'][-1]['file_id']
        path = 'tmp/' + id
        bot.download_file(id, path)
        return path
    else:
        return None