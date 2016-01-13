from .embeds import EmbedFactory


def get_url_safe(path, size='100x0', embeds=False):
    url_safe = ''
    if not 's3.amazonaws.com' in path:
        embed = EmbedFactory.get_embed(path, params=None)
        if embed is not None:
            video = embed.get_embed_dict()
            url_safe = video['thumbnail_url'] if embeds is False else video['embed_url']
        else:
            url_safe = path
    else:
        url_safe = path.replace('https', 'http')
    return url_safe
