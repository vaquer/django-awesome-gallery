from django.conf.urls import url, include
from tastypie.api import Api
from api import ResourceGallery, ResourceItem

gallery_api = Api(api_name='v1')
gallery_api.register(ResourceGallery())
gallery_api.register(ResourceItem())

urlpatterns = [

    #gallery
    url(r'^gallery/p/(?P<p>\d+)/?$', 'awesome_gallery.views.galleries', {}, 'galleries_view'),
    url(r'^gallery/api/', include(gallery_api.urls)),
    url(r'^gallery/?$', 'awesome_gallery.views.galleries', {}, 'galleries_view'),
    url(r'^gallery/(?P<gallery>[-_a-zA-Z0-9]+)/item/(?P<slug>[-_a-zA-Z0-9]+)/$', 'awesome_gallery.views.item_view_gal', {}, name='single_item'),
    url(r'^gallery/(?P<slug>[-_a-zA-Z0-9]+)/?$', 'awesome_gallery.views.gallery_view', {}, name='single_gallery'),
    url(r'^gallery/galeries/(?P<tag>[-_a-zA-Z0-9]+)/$', 'awesome_gallery.views.galleries_by_tag', {}, 'galleries_by_tag'),
    url(r'^gallery/(?P<gallery>[-_a-zA-Z0-9]+)/upload/$', 'awesome_gallery.views.add_item_ugc', {}, 'gallery_upload_ugc'),
    #admin
    url(r'^gallery/admin/add/key/?$', 'awesome_gallery.views.admin_add_item_aws', {}, 'widget_add_key'),
    url(r'^gallery/admin/add/description/key/?$', 'awesome_gallery.views.admin_adding_description_item', {}, 'widget_add_description_key'),
    url(r'^gallery/admin/delete/key/?$', 'awesome_gallery.views.admin_delete_item_aws', {}, 'widget_delete_key'),
    url(r'^gallery/admin/reorder/?$', 'awesome_gallery.views.admin_reorder_items', {}, 'widget_reorder_item'),
    url(r'^gallery/admin/item/status/(?P<status>[-_a-zA-Z0-9]+)/?$', 'awesome_gallery.views.admin_change_status_item', {}, 'widget_enabled_item'),
    # url(r'^fotos/(?P<gallery>[-_a-zA-Z0-9]+)/$'),
]
