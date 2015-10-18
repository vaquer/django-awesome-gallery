from tastypie.resources import ModelResource, ALL_WITH_RELATIONS, ALL
from tastypie import fields
from gallery.models import Gallery, Item
from django.http import HttpResponse
from django.conf.urls import url
from tastypie.cache import SimpleCache
from tastypie.serializers import Serializer


def build_content_type(format, encoding='utf-8'):
    """
    Appends character encoding to the provided format if not already present.
    """
    if 'charset' in format:
        return format

    return "%s; charset=%s" % (format, encoding)

class ResourceGallery(ModelResource):
    class Meta:
        queryset = Gallery.objects.all().order_by('-id')
        resource_name = 'gallery'
        filtering = {
            'slug': ALL,
            'id': ALL,
            'date': ['exact', 'lt', 'gt', 'lte', 'gte']
        }
        allowed_methods = ['get']
        serializer = Serializer(formats=['json'])
        cache = SimpleCache(timeout=10)

    def dehydrate(self, bundle):
        bundle.data = bundle.obj.dehydrate()
        bundle.data['resource_uri'] = '{0}{1}/'.format(self.get_resource_uri(), bundle.obj.id)
        return bundle

    def create_response(self, request, data, response_class=HttpResponse, **response_kwargs):
        """
        Extracts the common "which-format/serialize/return-response" cycle.

        Mostly a useful shortcut/hook.
        """
        desired_format = self.determine_format(request)
        serialized = self.serialize(request, data, desired_format)
        return response_class(content=serialized, content_type=build_content_type(desired_format), **response_kwargs)

    def get_object_list(self, request):
        return super(ResourceGallery, self).get_object_list(request).filter(enabled=True).order_by('-id').distinct()


class ResourceItem(ModelResource):
    gallery = fields.ToOneField('gallery.api.ResourceGallery', 'gallery', full=True)

    class Meta:
        queryset = Item.objects.all().order_by('-order')
        resource_name = 'item'
        filtering = {
            'slug': ALL,
            'gallery': ALL_WITH_RELATIONS,
            'date': ['exact', 'lt', 'gt', 'lte', 'gte']
        }
        allowed_methods = ['get']
        serializer = Serializer(formats=['json'])
        cache = SimpleCache(timeout=10)

    def prepend_urls(self):

        urls = super(ResourceItem, self).prepend_urls()
        return [
            url(r'^(?P<resource_name>)%s/(?P<id>[-_a-zA-Z0-9]+)/size/(?P<size>[-_a-zA-Z0-9]+)/' % (self._meta.resource_name), self.wrap_view('get_item_size'), name='gallery_api_get_item_size'),
            url(r'^(?P<resource_name>)%s/size/(?P<size>[-_a-zA-Z0-9]+)/' % (self._meta.resource_name), self.wrap_view('get_list_size'), name='gallery_api_get_list_size'),
        ]

    def get_item_size(self, request, **kwargs):
        self.method_check(request, allowed=['get'])

        id_itm = kwargs.get('id', None)
        size = kwargs.get('size', None)

        if id_itm is None:
            return self.create_response(request, {'error': 'Id is required.'})

        if size is None:
            return self.create_response(request, {'error': 'Size is required.'})

        item = Item.objects.get(id=id_itm)
        item_bundle = self.build_bundle(obj=item, request=request)
        item_bundle.data = item.dehydrate(size=size)
        item_bundle.data['resource_uri'] = '{0}{1}/'.format(self.get_resource_uri(), item.id)
        objects = []
        objects.append(item_bundle)

        obj_response = {
            'objects': objects
        }

        return self.create_response(request, obj_response)

    def get_list_size(self, request, **kwargs):
        size = kwargs.get('size', None)

        base_bundle = self.build_bundle(request=request)
        objects = self.obj_get_list(bundle=base_bundle, **self.remove_api_resource_names(kwargs))
        sorted_objects = self.apply_sorting(objects, options=request.GET)

        paginator = self._meta.paginator_class(request.GET, sorted_objects, resource_uri='{0}size/{1}/'.format(self.get_resource_uri(), size), limit=self._meta.limit, max_limit=self._meta.max_limit, collection_name=self._meta.collection_name)
        to_be_serialized = paginator.page()

        # Dehydrate the bundles in preparation for serialization.
        bundles = []

        for obj in to_be_serialized[self._meta.collection_name]:
            bundle = self.build_bundle(obj=obj, request=request)
            bundle.data = obj.dehydrate(size=size, excludes=[])
            bundles.append(bundle)

        to_be_serialized[self._meta.collection_name] = bundles
        to_be_serialized = self.alter_list_data_to_serialize(request, to_be_serialized)
        to_be_serialized['objects'] = bundles
        return self.create_response(request, to_be_serialized)

    def dehydrate(self, bundle):
        bundle.data = bundle.obj.dehydrate()
        bundle.data['resource_uri'] = '{0}{1}/'.format(self.get_resource_uri(), bundle.obj.id)
        return bundle

    def create_response(self, request, data, response_class=HttpResponse, **response_kwargs):
        """
        Extracts the common "which-format/serialize/return-response" cycle.

        Mostly a useful shortcut/hook.
        """
        desired_format = self.determine_format(request)
        serialized = self.serialize(request, data, desired_format)
        return response_class(content=serialized, content_type=build_content_type(desired_format), **response_kwargs)

    def get_object_list(self, request):
        return super(ResourceItem, self).get_object_list(request).filter(enabled=True).order_by('order').distinct()
