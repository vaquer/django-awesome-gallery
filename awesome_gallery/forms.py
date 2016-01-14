import os.path
from django import forms
from .models import Item, Gallery
from .form_fields import GalleryForeignKey
from .widgets import GalleryFKWidget, PreviewImageGall
from .aws import AWSManager
from django.conf import settings
from django.contrib.admin.widgets import FilteredSelectMultiple


class ItemForm(forms.ModelForm):
    preview = forms.CharField(widget=PreviewImageGall, label='Preview', required=False)
    image = forms.FileField(required=False, label='Imagen')
    url_video = forms.URLField(required=False, label='Video')

    def get_file_name(self):
        return os.path.basename(self.image.name)

    class Meta:
        model = Item
        fields = ('preview', 'image', 'url_video',)
        excludes = ['path']


class GalleryForm(forms.ModelForm):
    images = GalleryForeignKey(widget=GalleryFKWidget, label="Items", required=False)

    class Meta:
        model = Gallery
        fields = ('name', 'short_description', 'administrator', 'tags', 'enabled', 'images',)


class UGCItemForm(forms.ModelForm):
    image = forms.FileField(required=False, label='Imagen')
    url_video = forms.URLField(required=False, label='Video', widget=forms.TextInput(attrs={'class': 'form-control'}))

    def get_file_name(self):
        return os.path.basename(self.image.name)

    def save(self, force_insert=False, force_update=False, commit=True, gallery=None):
        model = super(UGCItemForm, self).save(commit=False)
        item_file = self.cleaned_data['image']

        if item_file is None and self.cleaned_data['url_video'].strip() == '':
            return
        elif item_file and self.cleaned_data['url_video'].strip() == '':
            aws = AWSManager(bucket=settings.AWS_BUCKET, api_key=settings.AWS_API_KEY, secret_key=settings.AWS_SECRET_KEY, host='s3.amazonaws.com')
            if not aws.upload(item_file.name, self.cleaned_data['image']):
                return
            model.path = aws.url(expires=30*90)
            model.key_name = aws.aws_key_name
        elif self.cleaned_data['url_video'].strip():
            model.path = self.cleaned_data['url_video']

        model.order = 0
        model.enabled = False
        model.display_title = True

        if gallery:
            model.gallery = gallery
        model.save()

    class Meta:
        model = Item
        fields = ('name', 'short_description', 'image', 'url_video',)
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'short_description': forms.Textarea(attrs={'class': 'form-control'})
        }
