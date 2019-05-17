from webpreview import web_preview
from string import Template

def grab_link_preview(url):
    try:
        title, description, image = web_preview(url)
        if description:
            t = '[pcclinkpreview url="$url" title="$title" image="$image"]$description[/pcclinkpreview]'
            return Template(t).safe_substitute(locals())
    except:
        print('error grabbing url')

    return Template('<a href="$url">$url</a>').substitute(dict(url=url))
