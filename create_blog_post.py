from wordpress_xmlrpc import Client
from wordpress_xmlrpc.compat import xmlrpc_client
from wordpress_xmlrpc.methods import media, posts, users
from wordpress_xmlrpc import WordPressPost
from wordpress_xmlrpc import Client
from wordpress_xmlrpc import AnonymousMethod
from pprint import pprint
from string import Template
import os
import magic
mime = magic.Magic(mime=True)

class GetPostByTelegramID(AnonymousMethod):
        method_name = 'plataformacc.getPostByTelegramID'
        method_args = ('msg_id',)


username_converts = {
    'rafaevangelista': 'tuttlebuttle',
}

username_ids = {}

admin_user = os.environ['WP_SUPERUSER']
admin_pass = os.environ['WP_SUPERUSER_PWD']

def create_blog_post(message):
    pprint(message['username'] + str(message['message_id']))
    username = message['username']
    if username in username_converts: username = username_converts[username]
    url = "http://" + username + ".plataforma.cc/xmlrpc.php"
    client = Client(url, admin_user, admin_pass)

    post = WordPressPost()

    if not username in username_ids:
        blogusers = client.call(users.GetUsers())
        username_ids[username] = next(u for u in blogusers if u.username == username).id

    post.user = username_ids[username]
    post.title = ''
    post.content = message['text']
    post.post_status = 'publish'

    if len(message['photo']):
        if post.content.find('[plataformacc_gallery]') == -1:
            post.content = post.content + '[plataformacc_gallery]'
            if message['caption']:
                post.content = post.content + message['caption'] + '[/plataformacc_gallery]'
    elif not len(message['text']):
        data = dict(id=str(message['message_id'][-1]), channel=message['username'])
        post.content = Template('[telegram_embed id="$id" channel="$channel"]').substitute(data)

    post_id = client.call(GetPostByTelegramID(message['message_id']))

    if (post_id == -1):
        print('multiple, wont update')
        return

    if (post_id == -2):
        print('has images, wont update')
        return

    if post_id and not message['edit']:
        print('already exists')
        return

    if not post_id:
        print('adding new')
        post_id = client.call(posts.NewPost(post))
        post.custom_fields = []
        for telegram_id in message['message_id']:
            post.custom_fields.append({ 'key': 'telegram_id', 'value': telegram_id })
            print('custom field', { 'key': 'telegram_id', 'value': telegram_id })

    if len(message['photo']):
        for photo in message['photo']:
            mimetype = mime.from_file(photo)
            ext = mimetype.split('/')[-1]
            data = {
                    'name': photo + '.' + ext,
                    'type': mimetype,  # mimetype
                    'post_id': post_id,

            }
            with open(photo, 'rb') as img:
                    data['bits'] = xmlrpc_client.Binary(img.read())
            response = client.call(media.UploadFile(data))
            post.wp_post_thumbnail = response['id']
            os.remove(photo)
        print('calling edit for photos', post_id)
        print(post)
    print('Updating', post_id, post)
    client.call(posts.EditPost(post_id, post))

