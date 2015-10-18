# import datetime
import urllib
import time
import json
from bs4 import BeautifulSoup
from dateutil.relativedelta import relativedelta
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User as AuthorModel
from django.core.cache import cache
from django.core import urlresolvers
from django.core.files import File
from django.core.files.images import get_image_dimensions
from django.db import models
from django.conf import settings
from django.utils.text import slugify
from django.utils.html import format_html
from .aws import AWSManager
from .decode import decode_path_admin, decode_path_gal, get_thumb_gal, get_url_safe
from .fields import ImageWithThumbsField

Languages = {
    "ES": {
        "gallery": {
            "name": "Nombre",
            "about": "Acerca de",
            "administrator": "Administrador",
            "date": "Fecha de creacion",
            "enabled": "Habilitado"
        },
        "item": {
            "name": "Nombre",
            "about": "Acerca de",
            "administrator": "Administrador",
            "date": "Fecha de creacion",
            "enabled": "Habilitado",
            "order": "Orden",
            "key_name": "Key AWS",
            "display_title": "Mostrar Titulo",
            "gallery": "Galeria"
        },
    },
    "EN": {
        "gallery": {
            "name": "Name",
            "about": "About",
            "administrator": "Administrator",
            "date": "Creation Date",
            "enabled": "Enabled"
        },
        "item": {
            "name": "Name",
            "image": "Image",
            "about": "Short Description",
            "administrator": "Administrator",
            "date": "Creation Date",
            "enabled": "Enabled",
            "order": "Order",
            "display_title": "Display Title",
            "gallery": "Gallery"
        },
    }
}


# Create your models here.
class Gallery(models.Model):
    name = models.CharField('{0}'.format(Languages[settings.LANGUAES_ALERTS]["gallery"]["name"]), max_length=200)
    slug = models.SlugField('Slug', max_length=200, editable=False, db_index=True)
    about = models.TextField('{0}'.format(Languages[settings.LANGUAES_ALERTS]["gallery"]["about"]), blank=True, null=True)

    administrator = models.ForeignKey(AuthorModel, verbose_name='{0}'.format(Languages[settings.LANGUAES_ALERTS]["gallery"]["administrator"]), null=True, blank=True)
    date = models.DateField('{0}'.format(Languages[settings.LANGUAES_ALERTS]["gallery"]["date"]), auto_now_add=True, editable=False)

    tags = models.ManyToManyField('{0}.{1}'.format(settings.APP_SOURCE, settings.TAGS_MODEL), verbose_name='Tags')
    ugc = models.BooleanField('UGC', default=False)

    high_definition = models.BooleanField('HD', default=True)
    enabled = models.BooleanField('{0}'.format(Languages[settings.LANGUAES_ALERTS]["gallery"]["enabled"]), default=True)

    def __unicode__(self):
        return u'{0}'.format(self.slug)

    @models.permalink
    def get_absolute_url(self):
        return ('single_gallery', (), {'slug': self})

    def gallery_permalink(self):
        link = '<a href="http://{0}{1}" target="_blank">http://{0}{1}</a>'.format(settings.FQDN, self.get_absolute_url())
        return format_html(link)
    gallery_permalink.allow_tags = True

    def first_item(self):
        first_item = None
        if self.count_enabled() > 0:
            self.check_order()
            try:
                first_item = self.items.get(order=1, enabled=True)
            except Item.DoesNotExists:
                pass

        return first_item

    def last_item(self):
        last_item = None
        if self.count_enabled() > 0:
            self.check_order()
            try:
                last_item = self.items.filter(enabled=True).order_by('order')[:-1]
            except Item.DoesNotExists:
                pass

        return last_item

    def first_foto_path_safe(self, size='470x0'):
        ff = self.first_foto()
        if ff is not None:
            return get_url_safe(ff.path, size=size)
        else:
            return None

    def first_foto_carousel(self):
        return self.first_foto_path_safe(size='670x0')

    def first_foto_thumb(self):
        return self.first_foto_path_safe(size="151x151")

    def first_foto_url(self):
        ff = self.first_foto()
        if ff is not None:
            return ff.get_absolute_url()
        else:
            return None

    def thumbnails_gallery(self):
        thumbs = None
        if self.count_enabled() > 0:
            thumb = self.items.all().order_by('order')[:5]

        return None

    def count(self):
        count = cache.get('count-gallery-{0}'.format(self.slug))
        if not count:
            count = self.items.count()
            cache.set('count-gallery', count, 60 * 60 * 12)

        return count

    def count_enabled(self):
        count = cache.get('count-gallery-enabled-{0}'.format(self.slug))
        if not count:
            count = self.items.filter(enabled=True).count()
            cache.set('count-gallery-enabled', count, 60 * 60 *12)

        return count

    def check_order(self):
        # Setup out of scope all unabled items
        Item.objects.filter(gallery__id=self.id, enabled=False).update(order=0)

        # Setup the correct order for all enabled items
        order = 0
        for single_item in Item.objects.filter(gallery__id=self.id, enabled=True).order_by('order'):
            if order:
                dif = single_item.order - order
                if dif != 1:
                    single_item.order = order + 1
                    single_item.save()
            order = single_item.order

    def related_galeries(self, json=False):
        key_cache = '{0}_related_galeries_news_m'.format(str(self.id)) if settings.IS_MOBILE is True else '{0}_related_galeries_news_v22'.format(str(self.id))
        galls = cache.get(key_cache)
        ffoto = None

        if galls is None:
            galls = []
            # Only Galleries of 3 months ago
            date_delta = self.date - relativedelta(months=2)

            for gallery in Gallery.objects.filter(tags__in=self.tags.all(), date__gt=date_delta, enabled=True).exclude(id=self.id).order_by('-id').distinct()[:4]:
                ffoto = gallery.first_foto_path_safe(size='150x0' if settings.IS_MOBILE is True else '370x250') 
                if ffoto is not None:
                    galls.append({'name': gallery.name[:40].encode('utf-8').replace('"', '\"'), 'permalink': gallery.get_absolute_url(), 'FQDN': settings.FQDN, 'count': gallery.count(), 'related_pic_url': ffoto})

            if len(galls) < 2:
                galls = []
                for gallery in Gallery.objects.filter(date__gt=date_delta, enabled=True).exclude(id=self.id).order_by('-id').distinct()[:4]:
                    ffoto = gallery.first_foto_path_safe(size='150x0' if settings.IS_MOBILE is True else '370x250') 
                    if ffoto is not None:
                        galls.append({'name': gallery.name[:40].encode('utf-8').replace('"', '\"'), 'permalink': gallery.get_absolute_url(), 'FQDN': settings.FQDN, 'count': gallery.count(), 'related_pic_url': ffoto})
            cache.set(key_cache, galls, 12 * 360) #12 hrs

        objects = { 'objects': galls }
        return json.dumps(objects) if json is True else objects

    def dehydrate(self, excludes=[], json=False):
        obj_responde = {
            'id': self.id,
            'slug': self.slug,
            'name': self.name,
            'name35': self.name[:35],
            'name15': self.name[:15],
            'about': self.about,
            'date': unicode(self.date) if json is True else self.date,
            'high_definition': self.high_definition,
            'enabled': self.enabled,
            'count': self.count(),
            'permalink': self.get_absolute_url(),
            'tags': [tag.tag for tag in self.tags.all()],
            'related_galeries': self.related_galeries()
        }

        if not 'first_foto' in excludes:
            ff = self.first_foto()
            obj_responde['first_foto'] = ff.dehydrate() if ff is not None else None

        return json.dumps(obj_responde) if json is True else obj_responde

    def save(self):
        if not self.id:
            slug = slugify(unicode(self.name))
            length_gals = Gallery.objects.filter(slug__istartswith=slug).count()
            if length_gals > 0:
                slug = '{0}-{1}'.format(slug, str(length_gals + 1))

            self.slug = slug
        super(Gallery, self).save()


class Item(models.Model):
    name = models.CharField('{0}'.format(Languages[settings.LANGUAES_ALERTS]["item"]["name"]), max_length=200)
    slug = models.SlugField('Slug', max_length=200, editable=False, unique=True, db_index=True)
    short_description = models.TextField('{0}'.format(Languages[settings.LANGUAES_ALERTS]["item"]["about"]))
    url_video = models.URLField('Path', max_length=250)
    image = ImageWithThumbsField('{0}'.format(Languages[settings.LANGUAES_ALERTS]["item"]["image"]), upload_to="django_awsm_gallery/items", sizes=settings.DJANGO_AWESOME_GALLERY_SIZES)
    order = models.IntegerField('{0}'.format(Languages[settings.LANGUAES_ALERTS]["item"]["order"]), db_index=True)

    date = models.DateField('{0}'.format(Languages[settings.LANGUAES_ALERTS]["item"]["date"]), auto_now_add=True, editable=False)
    tags = models.ManyToManyField('{0}.{1}'.format(settings.APP_SOURCE, settings.TAGS_MODEL), verbose_name='Tags')
    gallery = models.ForeignKey(Gallery, verbose_name='{0}'.format(Languages[settings.LANGUAES_ALERTS]["item"]["gallery"]), null=True, blank=True, related_name='items', related_query_name='gal_items')

    high_definition = models.BooleanField('HD', default=True)
    vertical = models.BooleanField('Vertical', default=False)
    enabled = models.BooleanField('{0}'.format(Languages[settings.LANGUAES_ALERTS]["item"]["enabled"]), default=True)
    display_title = models.BooleanField('{0}'.format(Languages[settings.LANGUAES_ALERTS]["item"]["display_title"]), default=False)

    def __unicode__(self):
        return u'{0}'.format(self.slug)

    @permalink
    def get_absolute_url(self):
        if self.gallery:
            return ('single_item', (), {'gallery': self.gallery.slug, 'slug': self.slug})
        else:
            return None

    def get_admin_url(self):
        content_type = ContentType.objects.get_for_model(self.__class__)
        return urlresolvers.reverse("admin:%s_%s_change" % (content_type.app_label, content_type.model), args=(self.id,))

    def item_preview(self):
        decode_path_html = decode_path_admin(self.path)
        return format_html(decode_path_html if decode_path_html is not None else self.path)
    item_preview.allow_tags = True

    def item_permalink(self):
        perma = self.get_absolute_url()
        if perma is not None:
            link = '<a href="http://{0}{1}" target="_blank">http://{0}{1}</a>'.format(settings.FQDN, self.get_absolute_url())
            return format_html(link)
        else:
            return "<p>Link no disponible</p>"
    item_permalink.allow_tags = True

    def get_foto_thumb(self, size='170x0', attrs=''):
        if not self.is_video():
            return self.image.url_170x0

    def get_foto_thumb_mobile(self, size='470x0'):
        if not self.is_video():
            return self.image.url_470x0

    def get_foto_thumb_safe_desktop(self, size='160x130'):
        if not self.is_video():
            return self.image.url_160x130

    def get_foto_safe_desktop(self, size='760x0'):
        if not self.is_video():
            return self.image.url_760x0

    def get_path_safe(self, size='100x0', embed=False):
        if not self.is_video():
            return self.image.url_100x0

    def get_url_thumbdesk(self):
        return get_url_safe(self.path, size="170x0")

    def get_foto_thumb_da(self):
        return get_url_safe(self.path, size='180x0')

    def get_foto_thumb_admin(self):
        return self.get_foto_thumb('200x140')

    def get_video_thumb_admin(self):
        return self.get_foto_size('192x133')

    def next_item(self):
        next = self.get_next()
        return next.get_absolute_url() if next is not None else None

    def prev_item_item(self):
        prev = self.get_previous()
        return prev.get_absolute_url() if prev is not None else None

    def get_next_item(self):
        next_item = cache.get('netx-item-to-{}'.format(self.id))

        if not next_item:
            try:
                next_item = Item.objects.get(gallery__id=self.gallery.id, order=self.order + 1, enabled=True)
                cache.set('netx-item-to-{}'.format(self.id), next_item, 60 * 60 * 12)
            except Item.DoesNotExists:
                next_item = None

        return next_item

    def get_previous_item(self):
        prev_item = cache.get('prev-item-to-{}'.format(self.id))

        if not prev_item:
            try:
                prev_item = Item.objects.get(gallery__id=self.gallery.id, order=self.order - 1, enabled=True)
                cache.set('prev-item-to-{}'.format(self.id), prev_item, 60 * 60 * 12)
            except Item.DoesNotExists:
                prev_item = None

        return prev_item

    def is_video(self):
        return False if not self.url_video else True

    def dehydrate(self, size='670x0', excludes=['gallery'], includes=[], json=False):
        width = int(size.split('x')[0])
        height = int(size.split('x')[1])

        if 'embeds' in includes:
            embed_size = '{0}x0'.format(str(width))
        
        obj_response = {
            'id': self.id,
            'slug': self.slug,
            'name': self.name,
            'about': self.about.encode('utf-8'),
            'name15': self.name[:15],
            'permalink': self.get_absolute_url(),
            'key_name': self.key_name,
            'order': self.order,
            'date': unicode(self.date) if json is True else self.date,
            'high_definition': self.high_definition,
            'enabled': self.enabled,
            'is_video': self.is_video(),
            'url_thumb': self.get_path_safe(size='670x0'),
            'url_thumb_151': self.get_path_safe(size='151x151'),
            'url_embed': self.get_path_safe(embed=True) if self.is_video() else None,
            'tags': [tag.tag for tag in self.tags.all()],
            'next': self.get_next().id if self.get_next() is not None else None,
            'prev': self.get_previous().id if self.get_previous() is not None else None,
            'display_title': self.display_title,
        }

        if self.gallery:
            if self.gallery.ugc:
                if self.about:
                    soup = BeautifulSoup(self.about)
                    obj_response['about'] = soup.get_text()

        if not 'gallery' in excludes:
            obj_response['gallery'] = self.gallery.dehydrate(excludes=['first_foto']) if self.gallery is not None else None

        if not 'sizes' in excludes:
            info_render = self.info_render_pic()
            obj_response['height'] = info_render['height']
            obj_response['width'] = info_render['width']
            obj_response['margin-left'] = 0
            obj_response['margin-top'] = 0
            obj_response['vertical'] = info_render['vertical']

        return json.dumps(obj_response) if json is True else obj_response

    def save(self):
        if not self.id:
            # Set the slug for the Item
            slug = slugify(unicode(self.name))
            count = Item.objects.filter(slug__startswith=slug).count()
            
            if count > 0:
                slug = '{0}-{1}'.format(slug, str(count))
                
            self.slug = slug

            # Set if the item is vertical
            if not self.url_video:
                self.vertical = True if self.image.width < self.image.height else False

        super(Item, self).save()
    current_gallery = None
