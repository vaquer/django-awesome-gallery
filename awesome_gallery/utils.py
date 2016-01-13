from awesome_gallery.models import Item, Gallery


def get_range_page(p, num_pages):
    after = ''
    before = ''
    add_p = True
    dif_up = num_pages - p

    if p - 3 > 0:
        iterations = 3 if p - 3 > 5 else p - 1
    else:
        iterations = p - 1

    while iterations > 0:
        before += str(p - iterations)
        if iterations > 1:
            before += ','
        iterations -= 1

    if before == '':
        add_p = False
        before = str(p)

    if p - 3 > 5:
        before = '1,2,...,{0}'.format(before)

    if p < num_pages:
        iterations = 4 if dif_up > 6 and p >= 1 else dif_up + 1
        iteration = 1
        while iteration < iterations:
            after += str(p + iteration)
            if (iterations - 1) > iteration:
                after += ','
            iteration += 1

        if after == '' and add_p:
            after = str(num_pages)
        else:
            add_p = True if p > 1 else False

        if iterations == 4:
            after = '{0},...,{1},{2}'.format(after, str(num_pages - 1), str(num_pages))
    else:
        add_p = False
        after = str(p)

    if add_p:
        after = '{0},{1}'.format(str(p), after)

    str_final = '{0},{1}'.format(before, after)

    return str_final.split(',')


def re_ordering(id):
    order = None
    items = Item.objects.filter(gallery__id=id, enabled=True).order_by('order')

    for item in items:
        if order is not None:
            dif = item.order - order
            if dif != 1:
                item.order = order + 1
                item.save()
        order = item.order
