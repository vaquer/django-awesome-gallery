from django import forms
from .widgets import GalleryFKWidget


class GalleryForeignKey(forms.Field):
    def formfield(self, *args, **kwargs):
        kwargs['widget'] = GalleryFKWidget(self.rel, using=kwargs.get('using'))
        return super(GalleryForeignKey, self).formfield(*args, **kwargs)
