from django.conf.urls import url, include
from tastypie.api import Api
from api import ResourceGallery, ResourceItem

gallery_api = Api(api_name='v1')
gallery_api.register(ResourceGallery())
gallery_api.register(ResourceItem())

urlpatterns = [

    #gallery
    url(r'^gallery/p/(?P<p>\d+)/?$', 'gallery.views.galleries', {}, 'galleries_view'),
    url(r'^gallery/api/', include(gallery_api.urls)),
    url(r'^gallery/?$', 'gallery.views.galleries', {}, 'galleries_view'),
    url(r'^gallery/(?P<gallery>[-_a-zA-Z0-9]+)/item/(?P<slug>[-_a-zA-Z0-9]+)/$', 'gallery.views.item_view_gal', {}, name='single_item'),
    url(r'^gallery/(?P<slug>[-_a-zA-Z0-9]+)/?$', 'gallery.views.gallery_view', {}, name='single_gallery'),
    url(r'^gallery/galeries/(?P<tag>[-_a-zA-Z0-9]+)/$', 'gallery.views.galleries_by_tag', {}, 'galleries_by_tag'),
    url(r'^gallery/(?P<gallery>[-_a-zA-Z0-9]+)/upload/$', 'gallery.views.add_item_ugc', {}, 'gallery_upload_ugc'),
    #admin
    url(r'^gallery/admin/add/key/?$', 'gallery.views.admin_add_item_aws', {}, 'widget_add_key'),
    url(r'^gallery/admin/add/description/key/?$', 'gallery.views.admin_adding_description_item', {}, 'widget_add_description_key'),
    url(r'^gallery/admin/delete/key/?$', 'gallery.views.admin_delete_item_aws', {}, 'widget_delete_key'),
    url(r'^gallery/admin/reorder/?$', 'gallery.views.admin_reorder_items', {}, 'widget_reorder_item'),
    url(r'^gallery/admin/enabled/item/?$', 'gallery.views.admin_enabled_item', {}, 'widget_enabled_item'),
    url(r'^gallery/admin/disabled/item/?$', 'gallery.views.admin_disabled_item', {}, 'widget_disabled_item'),
    # url(r'^fotos/(?P<gallery>[-_a-zA-Z0-9]+)/$'),
]
