import math
import json
import datetime
import re
import urllib
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404, HttpResponse
from django.conf import settings
from .models import Gallery, Item
from .utils import get_range_page
from .aws import AWSManager
from .forms import UGCItemForm
from .pagination import UberPaginator
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.html import format_html
from django.core.files.uploadedfile import UploadedFile
from django.db.models.loading import get_model
from dateutil.relativedelta import relativedelta
from django.core.files.images import get_image_dimensions
from django.core.files import File
from django.core.cache import cache
from django.db.models.loading import get_model


def galleries_by_tag(request, tag):
    Tag_model = get_model(settings.AWESOME_APP_BLOG_NAME, settings.AWESOME_APP_MODEL_TAG)

    if not tag:
        raise Http404

    try:
        tag = Tag_model.objects.get(tag=tag)
    except Exception, e:
        raise Http404

    gals_full_list = Gallery.objects.filter(tags__in=[tag], enabled=True).order_by('-id')
    check_number = re.compile('[^0-9]')
    p = request.GET.get('p', 1)
    if check_number.search(str(p)):
        return HttpResponseRedirect('/')
    p = int(p)

    up = UberPaginator(gals_full_list, settings.AWESOME_GALLERY_PAGINATOR_ELEMENTS)
    try:
        page = up.page(p)
    except (EmptyPage, InvalidPage):
        raise Http404
    nb = page.neighborhood()

    # Output
    context = {
        'gallerylist': page.object_list,
        'tag': tag,
        'what': 'foto',
        'up': up,
        'page_nb': nb,
        'page': page,
        'page_object': 'galeria',
    }

    return render(request, "gallery/{0}.html".format(settings.AWESOME_GALLERY_SEARCH_BY_TAGS_TEMPLATE), context)


# Create your views here.
def gallery_view(request, slug):
    if not slug:
        raise Http404

    gal = get_object_or_404(Gallery, slug=slug)

    page_obj = Paginator(gal.items.filter(enabled=True).order_by('order'), 20)
    page = page_obj.page(1)

    return render(request, '{gallery/{0}.html'.format(settings.AWESOME_GALLERY_GALLERY_TEMPLATE), {
        'gallery': gal,
        'related_galeries': gal.related_galeries(json=True),
        'fotos': page,
        'pg_obj': page_obj,
        # 'banner_url': settings.BANNER_URL,
        'item_list_json': [item_obj.dehydrate(excludes=['gallery'], json=True) for item_obj in page.object_list],
        'settings': settings})


def item_view_gal(request, gallery, slug):
    if not gallery or not slug:
        raise Http404

    next_item = None
    prev_item = None
    pics = []
    related_var = False
    Gal = page = page_obj = p = None

    if slug != "related-galeries-end" and slug != "related-galeries-init":
        pic = get_object_or_404(Item, gallery__slug=gallery, slug=slug)
        Gal = get_object_or_404(Gallery, slug=gallery)

        if Gal.items.count() == 0:
            raise Http404
        page_obj = Paginator(Gal.items.filter(enabled=True).order_by('order'), 20)
        page = page_obj.page(1)
    else:
        # Search Related Galeries
        related_var = True
        Gal = get_object_or_404(Gallery, slug=gallery)
        pic = Gal.last_foto() if slug == "related-galeries-end" else Gal.first_foto()

    if settings.GL_IS_MOBILE:
        if slug != "related-galeries-end":
            if slug == "related-galeries-init":
                next_item = "http://{0}{1}".format(settings.FQDN, pic.get_absolute_url())
            else:
                next_item = pic.next_item() or "http://{0}{1}/picture/related-galeries-end/".format(settings.FQDN, Gal.get_absolute_url())

        if slug != "related-galeries-init":
            if slug == "related-galeries-end":
                prev_item = "http://{0}{1}".format(settings.FQDN, pic.get_absolute_url())
            else:
                prev_item = pic.prev_item() or "http://{0}{1}/picture/related-galeries-init/".format(settings.FQDN, Gal.get_absolute_url())

        banner = None
        if pic.order % settings.SWIPE_COUNT_BANNER == 0:
            banner = settings.BANNER_URL

        context = {
            'foto': pic,
            'img': pic.get_foto_size('470x0', attrs=u'id="swipeft" alt="{0} - {1} - {2}"'.format(pic.name, Gal.name, settings.SITE_NAME).encode('utf-8')),
            'pic_470': pic.get_path_safe(size='470x0'),
            'pic_1024': pic.get_path_safe(size='1024x0'),
            'gallery': Gal,
            'next_item': next_item,
            'prev_item': prev_item,
            'banner_url': banner,
            'pics': Gal.related_galeries(),
            'related_url': related_var,
            'permalink': pic.get_absolute_url(),
            'data_pic': pic.info_render_pic(),
            'settings': settings,
        }
        template = 'mobile/{0}/item.html'.format(settings.SITE_NAME)
    else:
        context = {
            'gallery': Gal,
            'fotos': page,
            'pg_obj': page_obj,
            'p': p,
            'pic_rel': pic.id if pic is not None else None,
            'pic_obj': pic,
            'banner_url': settings.BANNER_URL,
            'settings': settings,
            'item_list_json': [item_obj.dehydrate(excludes=['gallery'], json=True) for item_obj in page.object_list],
            'related_galeries': Gal.related_galeries(json=True)
        }
        template = 'desktop/{0}/gallery.html'.format(settings.SITE_NAME)

    return render(request, template, context)


def galleries(request, p=None):
    if p == 1:
        return redirect('/gallery/')

    if p is None:
        p = 1

    page_obj = Paginator(Gallery.objects.filter(enabled=True).order_by('-id'), 20)
    gallery_sample = Gallery.objects.all()[Gallery.objects.all().count() - 1:]
    page = page_obj.page(p)

    range_paginator = get_range_page(int(p), page_obj.num_pages)

    return render(request, 'gallery/{0}.html'.format(settings.AWESOME_GALLERY_GALERIES_TEMPLATE), {
        'p': p,
        'po': page_obj,
        'page': page,
        'galleries': page.object_list,
        'settings': settings,
        'gallery_sample': gallery_sample,
        'range_paginator': range_paginator,
    })

def add_item_ugc(request, gallery):
    do_upload = render_form = True
    gallery_obj = response = None
    correct_upload = False

    try:
        gallery_obj = Gallery.objects.get(slug=gallery)
    except Exception:
        render_form = False
        response = "Galeria inexistente"

    if request.method == "POST" and render_form:
        form = UGCItemForm(request.POST, request.FILES)

        if do_upload and form.is_valid():
            form.save(gallery=gallery_obj)
            correct_upload = True
            form = None

    elif request.method == "GET" and render_form:
        if gallery_obj.ugc:
            form = UGCItemForm()
            response = None
        else:
            form = None
            response = "No se permite la subida de archivos en esta galeria"
    else:
        form = None
        if gallery_obj:
            if not gallery_obj.ugc:
                response = "No se permite la subida de archivos en esta galeria"

    return render(request, '{0}/{1}/upload.html'.format("desktop" if settings.GL_IS_MOBILE is False else "mobile", settings.SITE_NAME),{
        'form': form,
        'response': response,
        'gallery': gallery,
        'correct': correct_upload
        })

@staff_member_required
def admin_add_item_aws(request):
    if request.method == "POST":
        output = {}
        file_obj = None

        # Get the image file on the request
        if request.FILES.get(u'files[]', None):
            file_request = request.FILES.get(u'files[]')
            file_obj = UploadedFile(file_request)

        video = request.POST.get('video', None)
        
        if not video and not file_obj:
            output['error'] = "Error: Error at upload file, can't recive the file"

        if not output.get('error', False):
            model_fields = request.POST + {'image':file_obj, 'url_video':  video, 'enabled': True}
            # Remove tags from initial fields
            model_fields.pop('tags', None)
            model_fields['high_definition'] = True if model_fields['high_definition'].strip() else False
            model_fields['order'] = int(model_fields['order'])

            # Creating the new Item
            item = Item(**model_fields)
            item.save()

            # Insert all tags
            ModelTag = get_model(settings.AWESOME_APP_BLOG_NAME, settings.AWESOME_APP_MODEL_TAG)
            for tag in request.POST.get('tags', '').split(','):
                if tag.strip():
                    try:
                        model_tag_instance = ModelTag.objects.get(tag=tag)
                    except:
                        model_tag_instance = ModelTag(tag=tag)

                    model_tag_instance.save()
                    item.tags.add(model_tag_instance)
            item.save()
            output['item'] = {"path": path_aws, "key_name": aws.aws_key_name, "html": item_model.get_foto_thumb(size), "id": item_model.id, "order": item_model.order, "admin": item_model.get_admin_url(), 'isVideo': False}

        json_obj = json.dumps(output)
        return HttpResponse(json_obj, content_type="application/json")
    else:
        raise Http404


@staff_member_required
def admin_delete_item_aws(request):
    if request.method != "POST":
        raise Http404

    output = {}
    key_name = None
    list_items = [int(itm_i) for itm_i in request.POST.get('id_list', '-1').split(',')]

    # Delete all items in the list from gallery
    try:
        Item.objects.filter(id__in=list_items).delete()
    except Exception, e:
        output['error'] = 'Error: {0}'.format(e)      

    if not output.get('error', False):
        output['ok'] = 'Ok, {} processed items'. format(str(len(ids_list)))

    json_obj = json.dumps(output)
    return HttpResponse(json_obj, content_type="application/json")


@staff_member_required
def admin_change_status_item(request, status='false'):
    if request.method != 'POST':
        raise Http404

    if 'list_items' not in request.POST:
        raise Http404

    output = {}
    list_items = request.POST.get('list_items', '')
    status_item = True if request.POST.get('item_status' , False) or request.POST.get('item_status' , False) == 'true' else False

    if not list_items:
        output['error'] = 'No hay items para habilitar'

    if not output.get('error', False):
        list_items = [int(item) for item in list_items.split(',')]

        # Enabling all the items in list
        Item.objects.filter(id__in=list_items).update(enabled=status_item)

        output['ok'] = 'Items Habilitados : {0}'.format(str(len(list_items)))

    json_response = json.dumps(output)
    return HttpResponse(json_response, content_type="application/json")


@staff_member_required
def admin_adding_description_item(request): 
    if request.method != 'POST':
        raise Http404

    output = {}
    item_model = get_object_or_404(Item, id=request.POST.get('item_id'))

    item_model.about = urllib.unquote(request.POST.get('descript_item_updt')).encode('utf-8')
    item_model.save()
    output['ok'] = 'Descricion agregada'

    json_response = json.dumps(output)
    return HttpResponse(json_response, content_type='application/json')


def admin_reorder_items(request):
    if request.method == 'POST':
        id_list = [int(itm) if itm else 0 for itm in request.POST.get('id_list').split(',')]
        order = 1
        response = {}
        processed = ''

        for item_id in id_list:
            if processed != '':
                processed += ','
            processed += str(item_id)
            item_object = Item.objects.get(id=item_id)
            item_object.order = order
            item_object.save()
            order += 1

        response['ok'] = "{0} Items processed".format(len(id_list))
        response['lista'] = processed

        json_response = json.dumps(response)
        return HttpResponse(json_response, content_type="application/json")
    else:
        raise Http404
