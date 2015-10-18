import re
import urlparse
from django import template
from django.utils.html import strip_tags
from django.template import Context, loader
from django.conf import settings
from gallery.models import Gallery

register = template.Library()

@register.filter(name='gallery_embed', is_safe=True)
def gallery_embed(value):
    gallery = None
    if value:
        response_value = value
        strip_text = strip_tags(value.replace(r"<br>", r" ").replace(r"<br />", r" ").replace(r"</br>", r" "))
        # Obtenemos el template html del embed
        template = loader.get_template('embed/embed.html')

        for urlgroup in re.findall(ur'(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:\'".,<>?\xab\xbb\u201c\u201d\u2018\u2019]))', strip_text):
            html = ''
            string_url = strip_tags(urlgroup[0]).strip()
            parse_url = urlparse.urlparse(string_url)

            if settings.BASE_FQDN in parse_url.netloc and 'gallery' in parse_url.path:
                slug = parse_url.path.split('/')[2]

                try:
                    try:
                        gallery = Gallery.objects.get(slug=slug)
                    except:
                        return value

                    c = Context({'slug': gallery.slug, 'id': gallery.id, 'name': gallery.name[:30]})
                    # Rellenamos el template con los datos del contexto y obtenemos el render
                    html = u'{0}'.format(template.render(c))

                    response_value = re.sub(ur'((?i)[^"])(%s)' % string_url.replace('?', '\?'), r'\1%s' % html, response_value)
                except Exception, e:
                    raise '{0} slug:{1}'.format(e, gallery.name.encode('utf-8') if gallery else '')

        return response_value
    else:
        return value

@register.filter(name='undo_slug', is_safe=True)
def undo_slug(value):
    return value.replace("-", " ")
