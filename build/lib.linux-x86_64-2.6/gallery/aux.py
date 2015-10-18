from gallery.models import Item, Gallery

def check_order(slug):
        gall_obj = Gallery.objects.get(slug=slug)
        order = 0
        items_unabled = Item.objects.filter(gallery__id=gall_obj.id, enabled=False).order_by('order')

        for single_item_unabled in items_unabled:
            if single_item_unabled.order > 0:
                single_item_unabled.order = 0
                single_item_unabled.save()

        items_enabled = Item.objects.filter(gallery__id=gall_obj.id, enabled=True).order_by('-order')
        for single_item in items_enabled:
            if order is not None:
                dif = single_item.order - order
                if dif != 1:
                    single_item.order = order + 1
                    single_item.save()
            order = single_item.order