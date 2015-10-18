from django import forms
from django.utils.safestring import mark_safe
from django.template import loader, Context
from django.conf import settings
from gallery.models import Item


class GalleryFKWidget(forms.Widget):
    def __init__(self, *args, **kwargs):
        super(GalleryFKWidget, self).__init__(*args, **kwargs)

    def render(self, name, value, *args, **kwargs):
        list_items, id_gallery, list_ids_item = [], '', []

        if value:
            # Get items from a gallery already saved in DB
            if type(value) is not unicode:
                id_gallery = value.id
                list_items = Item.objects.filter(gallery__id=value.id).order_by('order')
            # Get items from a gallery that not yet saved in DB
            elif type(value) is unicode and value != u'':
                list_ids_item = [int(id_item.strip()) for id_item in value.split(',')]
                list_items = Item.objects.filter(id__in=list_ids_item).order_by('order')

        # Is a user gallery
        if list_items:
            if value.ugc:
                list_items = list_items[:70]

        context_obj = Context({'list_items': list_items, 'settings': settings, 'id_gallery': id_gallery})

        template = loader.get_template('admin.html')
        html = template.render(context_obj)

        return mark_safe(unicode(html))

    class Media:
        js = (
            '/static/js/gallery/lib/load-image/load-image.all.min.js',
            '/static/js/libs/require/require-min.js',
            '/static/gallstatic/js/amd_config.js',
        )
        css = {'all': (
            '/static/gallstatic/css/admin/gallery_admin.css?2015030847',
            '/static/gallstatic/js/lib/jquery/jquery-ui-1.11.2.custom/jquery-ui.min.css',
            '/static/css/bootstrap/bootstrap.min.css',
        )}


class PreviewImageGall(forms.Widget):
    def __init__(self, *args, **kwargs):
        return super(PreviewImageGall, self).__init__(*args, **kwargs)

    def render(self, name, value, *args, **kwargs):
        html = ''
        if value is not None:
            html = '{0}'.format(value.get_foto_size('400x300'))

        return mark_safe(unicode(html))
