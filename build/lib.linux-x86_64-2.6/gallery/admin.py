from django.contrib import admin
from django.conf import settings
from gallery.models import Gallery, Item
from gallery.forms import ItemForm, GalleryForm
from gallery.aws import AWSManager


class ItemAdmin(admin.ModelAdmin):
    form = ItemForm
    list_display = ('name', 'about', 'item_permalink', 'item_preview', 'high_definition', 'vertical', 'enabled')
    save_on_top = True
    search_fields = ['name', 'slug']
    ordering = ('-date', )
    raw_id_fields = ('tags', )
    fieldsets = (
        (None, {"fields": ('name', 'about', 'administrator', 'order')}),
        ('Items', {"fields": ('img', 'video_source', 'preview')}),
        ('Clasificacion', {"fields": ('tags',)}),
        ('Extra', {"fields": ('display_title', 'high_definition', 'enabled')})
    )

    def get_form(self, request, obj=None, **kwargs):
        form = super(ItemAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['preview'].initial = obj if obj is not None else None
        return form

    def save_model(self, request, obj, form, change):
        path_request = request.FILES.get('img', None)

        if path_request is not None:
            aws = AWSManager(bucket=settings.AWS_BUCKET, api_key=settings.AWS_API_KEY, secret_key=settings.AWS_SECRET_KEY, host='s3.amazonaws.com')
            if aws.upload(path_request.name, form.cleaned_data['img']):
                obj.path = aws.url(expires=30)
                obj.key_name = aws.aws_key_name
        elif form.cleaned_data['video_source'] != '':
            obj.path = form.cleaned_data['video_source']

        obj.save()

    class Media:
            js = (
                '/static/js/libs/jquery/jquery.js',
                '//api.filepicker.io/v1/filepicker.js',
                '/static/js/libs/tiny-mce/3.5.11/tiny_mce.js',
                '/static/js/libs/tiny-mce/textareas.js',
                'http://yui.yahooapis.com/combo?2.7.0/build/utilities/utilities.js&2.7.0/build/button/button-min.js&2.7.0/build/container/container-min.js&2.7.0/build/cookie/cookie-min.js',
                '/static/js/admin/admin.js'
            )
admin.site.register(Item, ItemAdmin)


# Register your models here.
class GalleryAdmin(admin.ModelAdmin):
    form = GalleryForm
    list_display = ('name', 'about', 'date', 'gallery_permalink', 'high_definition', 'enabled')
    save_on_top = True
    search_fields = ['name', 'slug']
    ordering = ('-date', )
    raw_id_fields = ('tags', )

    def save_model(self, request, obj, form, change):
        obj.save()
        # Obtaining the list of images in POST array
        id_string_list = request.POST.get('images', None)

        if id_string_list.strip():
            item_model = None
            # If a single model doesn't have relation to the gallery, will set up
            for item_id in id_string_list.split(','):
                try:
                    item_model = Item.objects.get(id=int(item_id))
                    if not item_model.gallery_id:
                        item_model.gallery_id = obj.id
                        item_model.save()
                except Exception:
                    continue

        # Checking the order of items, fixing problems in secuence
        obj.check_order()

    def get_form(self, request, obj=None, **kwargs):
            form = super(GalleryAdmin, self).get_form(request, obj, **kwargs)
            # Setting the values to widget Gallery
            form.base_fields['images'].initial = obj or None
            return form

    class Media:
            js = (
                '/static/js/libs/jquery/jquery.js',
                '//api.filepicker.io/v1/filepicker.js',
                '/static/js/libs/tiny-mce/3.5.11/tiny_mce.js',
                '/static/js/libs/tiny-mce/textareas.js?545',
                '/static/js/lib/jquery/jquery-ui-1.11.2.custom/jquery-ui.min',
                '/static/js/lib/jquery/jquery.upload',
                '/static/js/lib/canvas-to-blob/canvas-to-blob.min',
                '/static/js/lib/load-image/load-image-meta',
                '/static/js/lib/load-image/load-image',
                '/static/js/lib/load-image/load-image-exif-map',
                '/static/js/lib/load-image/load-image-exif',
                '/static/js/lib/load-image/load-image-ios',
                '/static/js/lib/jquery/jquery.ui.widget',
                '/static/js/lib/jquery/jquery.iframe-transport',
                '/static/js/lib/jquery/jquery.fileupload-process',
                '/static/js/lib/jquery/jquery.fileupload-image',
                '/static/js/lib/jquery/jquery.fileupload',
                '/static/js/libs/underscore/underscore-min',
                '/static/js/libs/backbone/backbone-min',
                '/static/js/libs/bootstrap/bootstrap.min',
                '/static/js/admin.js'
            )
admin.site.register(Gallery, GalleryAdmin)
