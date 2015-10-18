# -*- encoding: utf-8 -*-
import cStringIO
import hmac
import re
import urllib
import types

from PIL import Image, ImageFilter
from django.db.models import ImageField
from django.db.models.fields.files import ImageFieldFile
from django.core.files.base import ContentFile
from django.conf import settings

"""
django-thumbs by Antonio Melé
http://django.es
Modificado para RG: Roberto Alamos <ralamosm@redgol.cl>, Francisco Lavin <fcolavin@gmail.com>
Modificado para uso con thumbr.io: Francisco Vaquero <akura11.tt@gmail.com>
"""
def _get_Thumbrio(url, size):
    if re.match(r'^[0-9]+x[0-9]+', size):
        base_url = settings.THUMBRIO_BASE_URLS[0]
        urlTemp = url.decode('utf-8')
        nameThumbrio = urlTemp.rsplit('.', 1)
        nameThumbrio = nameThumbrio[0]
        nameThumbrio = nameThumbrio.split('/')
        nameThumbrio = nameThumbrio[len(nameThumbrio) - 1]
        nameThumbrio = '%s.jpg' % (nameThumbrio)

        temp = size.split('x')
        width = temp[0]
        height = temp[1]

        unprefixed_url = re.sub(r'^http://', '', urlTemp).encode('utf-8')
        encoded_url = urllib.quote(unprefixed_url, safe='/-_.')
        encoded_size = urllib.quote(size, safe='/-_.')
        encoded_thumb_name = urllib.quote(nameThumbrio.encode('utf-8'), safe='/-_.')
        if height == '0':
            path = '%s/%sx/%s' % (encoded_url, width, encoded_thumb_name)
        else:
            path = '%s/%sc/%s' % (encoded_url, encoded_size, encoded_thumb_name)

        # path = '%s/%s' % (settings.THUMBRIO_API_KEY, path)

        path = path.replace('//', '%2F%2F')
        token = hmac.new(settings.THUMBRIO_SECRET_KEY, base_url + path).hexdigest()
        return '%s%s/%s' % (base_url, token, path)


class ImageWithThumbsFieldFile(ImageFieldFile):
    """
    See ImageWithThumbsField for usage example
    """
    def __init__(self, *args, **kwargs):
        super(ImageWithThumbsFieldFile, self).__init__(*args, **kwargs)


    def __getattr__(self, attr):
        if re.match(r'^url_[0-9]+x[0-9]+', attr):
            base_url = settings.THUMBRIO_BASE_URLS[0]
            try:
                urlTemp = (getattr(self, 'url') if getattr(self, 'url') != '' else 'http://s.rgcdn.net/filez/img/1.gif')
            except Exception, e:
                setattr(self, attr, 'http://s.rgcdn.net/filez/img/1.gif')
                return getattr(self, attr)
            nameThumbrio = urlTemp.rsplit('.', 1)
            nameThumbrio = nameThumbrio[0]
            nameThumbrio = nameThumbrio.split('/')
            nameThumbrio = nameThumbrio[len(nameThumbrio) -1]
            nameThumbrio = '%s.jpg' % (nameThumbrio)
            sizeTemp = attr.split('_')
            sizeTemp = sizeTemp[1]
            temp = sizeTemp.split('x')

            width = temp[0]
            height = temp[1]

            def _thumbrio_quote(s):
                    return urllib.quote(s, safe='/-_.')

            def _getThumbrio(self):
                unprefixed_url = re.sub(r'^http://', '', urlTemp).decode('utf-8').encode('utf-8')
                encoded_url = _thumbrio_quote(unprefixed_url)
                encoded_size = _thumbrio_quote(sizeTemp)
                encoded_thumb_name = _thumbrio_quote(nameThumbrio)
                if height == '0':
                    path = '%s/%sx/%s' % (encoded_url, width, encoded_thumb_name)
                else:
                    path = '%s/%sc/%s' % (encoded_url, encoded_size, encoded_thumb_name)

                # path = '%s/%s' % (settings.THUMBRIO_API_KEY, path)

                path = path.replace('//', '%2F%2F')
                token = hmac.new(settings.THUMBRIO_SECRET_KEY, base_url + path).hexdigest()
                return '%s%s/%s' % (base_url, token, path)

            setattr(self, attr, _getThumbrio(self))
            return getattr(self, attr)
        else:
            return ImageFieldFile.__getattr__(self, attr)


class ImageWithThumbsField(ImageField):
    attr_class = ImageWithThumbsFieldFile
    """
    Usage example:
    ==============
    photo = ImageWithThumbsField(upload_to='images', sizes=((125,125),(300,200),)
    To retrieve image URL, exactly the same way as with ImageField:
        my_object.photo.url
    To retrieve thumbnails URL's just add the size to it:
        my_object.photo.url_125x125
        my_object.photo.url_300x200
    Note: The 'sizes' attribute is not required. If you don't provide it,
    ImageWithThumbsField will act as a normal ImageField
    How it works:
    =============
    For each size in the 'sizes' atribute of the field it generates a
    thumbnail with that size and stores it following this format:
    available_filename.[width]x[height].extension
    Where 'available_filename' is the available filename returned by the storage
    backend for saving the original file.
    Following the usage example above: For storing a file called "photo.jpg" it saves:
    photo.jpg          (original file)
    photo.125x125.jpg  (first thumbnail)
    photo.300x200.jpg  (second thumbnail)
    With the default storage backend if photo.jpg already exists it will use these filenames:
    photo_.jpg
    photo_.125x125.jpg
    photo_.300x200.jpg
    Note: django-thumbs assumes that if filename "any_filename.jpg" is available
    filenames with this format "any_filename.[widht]x[height].jpg" will be available, too.
    To do:
    ======
    Add method to regenerate thubmnails
    """
    def __init__(self, verbose_name=None, name=None, width_field=None, height_field=None, sizes=None, **kwargs):
        self.verbose_name = verbose_name
        self.name = name
        self.width_field = width_field
        self.height_field = height_field
        self.sizes = sizes
        super(ImageField, self).__init__(**kwargs)

    def south_field_triple(self):
        """
        Returns a suitable description of this field for South.
        """
        # We'll just introspect the _actual_ field.
        from south.modelsinspector import introspector
        field_class = 'awesome_gallery.fields.ImageWithThumbsField'
        args, kwargs = introspector(self)
        # That's our definition!
        return (field_class, args, kwargs)