from daleideas.cms.embedmedia import MediaDecoder
from daleideas.embeds import EmbedFactory
from daleideas.fields import _get_Thumbrio


def decode_path_admin(path):
    decoder = MediaDecoder.get_decoder(path, 'admin_list', None)

    if decoder is not None:
        return decoder.decode()
    else:
        url_safe = path.replace('https', 'http')
        return '<img src="{0}" />'.format(_get_Thumbrio(url_safe, '400x0'))


def decode_path_gal(path, size=None, attrs='', vertical=False, style='', classes=''):
    decoder = MediaDecoder.get_decoder(path, 'gal', None)

    if decoder is not None:
        return decoder.decode(size=size, attrs=attrs)
    else:
        # if not 's3.amazonaws.com' in path:
        #     return None
        # else:
        url_safe = path.replace('https', 'http')
        return '<img class="{5} {3}" src="{0}" {1} style="{2} {4}"/>'.format(_get_Thumbrio(url_safe, '100x0' if size is None else '{0}x0'.format(size.split('x')[0])), attrs, 'width: {0}px; height: {1}px;'.format(size.split('x')[0], size.split('x')[1]) if size.split('x')[1] != '0' else '', 'imgShow vertical' if vertical is True else '', style, classes)


def get_thumb_gal(path, size='100x0', attrs=''):
    return '<img src="{0}" {1} {2}/>'.format(get_url_safe(path, size), attrs, 'style="width: {0}px; height: {1}px;"'.format(size.split('x')[0], size.split('x')[1]) if size.split('x')[1] != '0' else '')


def get_url_safe(path, size='100x0', embeds=False):
    url_safe = ''
    if not 's3.amazonaws.com' in path:
        embed = EmbedFactory.get_embed(path, params=None)
        if embed is not None:
            video = embed.get_embed_dict()
            # if video:
            url_safe = video['thumbnail_url'] if embeds is False else video['embed_url']
            # else:
            #     url_safe = path
        else:
            url_safe = path
    else:
        url_safe = path.replace('https', 'http')
    return _get_Thumbrio(url_safe, size) if not embeds else url_safe
