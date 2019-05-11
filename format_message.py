from urlextract import URLExtract
from string import Template
from telepot.text import apply_entities_as_html
from grab_link_preview import grab_link_preview
import re

extractor = URLExtract()

def format_message(updates):
    parts = []
    for update in updates:
        if not 'text' in update: continue
        if 'entities' in update and len(list(ent for ent in update['entities'] if ent['type'] != 'url')):
            text = apply_entities_as_html(update['text'], update['entities'])
            urls = list(url for url in extractor.find_urls(text) if url.find('twitter.com') == -1)
        else:
            text = update['text']
            urls = extractor.find_urls(text)
            for url in urls:
                furl = url
                if not url.startswith('http'): furl = 'http://' + url
                text = text.replace(url, Template('<a href="$url">$url</a>').substitute(dict(url=furl)))
        if len(urls):
            preview = grab_link_preview(urls[0])
            if preview: text += '\n' + preview    

        if 'forward_from_chat' in update:
            data = {
                'from': update['forward_from_chat']['username'],
                'text': text
            }
            text = Template('[plataformacc_forwarded_from from="$from"]$text[/plataformacc_forwarded_from]').substitute(data)

        parts.append(text)
    return '\n\n'.join(parts)
