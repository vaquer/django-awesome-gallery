import os.path
from django import forms
from gallery.models import Item, Gallery
from gallery.fields import GalleryForeignKey
from gallery.widgets import GalleryFKWidget, PreviewImageGall
from gallery.aws import AWSManager
from django.conf import settings


class FormInput(forms.Form):
    imageWidget = forms.FileField()


class ItemWidgetForm(forms.ModelForm):
    class Meta:
        model = Item
        excludes = ['gallery', 'key_name']


class ItemForm(forms.ModelForm):
    preview = forms.CharField(widget=PreviewImageGall, label='Preview', required=False)
    img = forms.FileField(required=False, label='Imagen')
    video_source = forms.URLField(required=False, label='Video')

    def get_file_name(self):
        return os.path.basename(self.img.name)

    class Meta:
        model = Item
        excludes = ['path']


class GalleryForm(forms.ModelForm):
    images = GalleryForeignKey(widget=GalleryFKWidget, label="Items", required=False)

    class Meta:
        model = Gallery


class UGCItemForm(forms.ModelForm):
    img = forms.FileField(required=False, label='Imagen')
    video_source = forms.URLField(required=False, label='Video', widget=forms.TextInput(attrs={'class': 'form-control'}))

    def get_file_name(self):
        return os.path.basename(self.img.name)

    def save(self, force_insert=False, force_update=False, commit=True, gallery=None):
        model = super(UGCItemForm, self).save(commit=False)
        item_file = self.cleaned_data['img']

        if item_file is None and self.cleaned_data['video_source'].strip() == '':
            return
        elif item_file and self.cleaned_data['video_source'].strip() == '':
            aws = AWSManager(bucket=settings.AWS_BUCKET, api_key=settings.AWS_API_KEY, secret_key=settings.AWS_SECRET_KEY, host='s3.amazonaws.com')
            if not aws.upload(item_file.name, self.cleaned_data['img']):
                return
            model.path = aws.url(expires=30*90)
            model.key_name = aws.aws_key_name
        elif self.cleaned_data['video_source'].strip():
            model.path = self.cleaned_data['video_source']

        model.order = 0
        model.enabled = False
        model.display_title = True

        if gallery:
            model.gallery = gallery
        
        model.save()

    class Meta:
        model = Item
        fields = ['name', 'about']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'about': forms.Textarea(attrs={'class': 'form-control'})
        }
