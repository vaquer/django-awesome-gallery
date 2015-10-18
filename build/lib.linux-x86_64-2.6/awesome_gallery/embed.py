from gallery.models import Item, Gallery
from django.utils import simplejson

def context_embed(slug):
    galleryDehydrated = {}
    if slug and slug != 'undefined' and slug != 'null':
        item = Item.objects.get(slug=slug)
        itemDehydrated = item.dehydrate(excludes=[])
        itemDehydrated['date'] = unicode(item.date)
        if itemDehydrated.get('gallery', None):
            itemDehydrated['gallery']['date'] = unicode(item.date)
            galleryDehydrated = itemDehydrated['gallery']

        return simplejson.dumps({'item': itemDehydrated, 'gallery': galleryDehydrated })
    else:
        return None