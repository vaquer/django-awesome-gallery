define(['jquery', 'underscore', 'backbone', 'GalSettings', 'gallery/widgets/views/item', 'items_list_json', 'gallery/widgets/models/gallery', 'gallery/widgets/collections/items', 'hgn!gallery/templates/desktop/galleryItem', 'hgn!gallery/templates/desktop/item'], 
    function ($, _, BB, Settings, Item, ItemList, GalleryModel, ItemsCollection, ItemTemplate, ItemSingletemplate){
    return BB.View.extend({
        el: $('#galerias'),
        itemsCollectionObj: null,
        galleryObj: null,
        isLoading: false,
        endRequests: false,
        _triggerPoint: 1500,
        events: {
            'click div.listItem': 'SingleItemEvent'
        },
        initialize: function(){
            _.bindAll(this, '_checkScroll')
            //Convertimos la lista de items a una lista de objetos JSON
            if(ItemList.length > 1){
                ItemList = _.reduce(ItemList, function(prev_el, next_el){
                    if(_.isString(prev_el)){
                        prev_el = [JSON.parse(prev_el)];
                    }
                    prev_el.push(JSON.parse(next_el));
                    return prev_el;
                });
            }else if(ItemList.length === 1){
                ItemList = JSON.parse(ItemList);
            }
            
            // Cargando el modelo de galeria
            this.galleryObj = new GalleryModel({
                'id': Settings.Gallery.id,
                'slug': Settings.Gallery.slug,
                'permalink': Settings.Gallery.permalink,
                'related_galeries': Settings.Gallery.related_galeries,
                'name': Settings.Gallery.name,
                'count': Settings.Gallery.count
            });

            if(this.galleryObj.get('count') < 20){
                this.endRequests = true;
            }
            // Cargar la lista de items
            this.itemsCollectionObj = new ItemsCollection(ItemList, {'gallery': Settings.Gallery.slug, 'size': '670x0'});
            $(window).scroll(this._checkScroll);
        },
        render: function(){
            //Revisamos si se debe cargar una imagen
            if(Settings.Gallery){
                if(typeof Settings.Gallery.picRel !== 'undefined'){
                    this.showSingleItem(Settings.Gallery.picRel);
                }
            }

            return this;
        },
        SingleItemEvent: function(el){
            this.showSingleItem($(el.currentTarget).attr('data-di'));
            return false;
        },
        _loadItems: function(){
            var self = this;
            // Cambiar el estado de la carga
            this.isLoading = true;
            // Cargar los nuevos items
            this.itemsCollectionObj.fetch({success: function(collection, response){
                if(!collection.options.next){
                    self.endRequests = true;
                }
                $('#galerias').append(_.reduce(collection.models.slice((-1 * response.objects.length)), function(prev_el, next_el){
                    if(!_.isString(prev_el)){
                        prev_el = (!self._checkItemExists(next_el.get('id')) ? ItemTemplate(_.defaults({'CLASS_ITEM': Settings.Gallery.el} ,prev_el.toJSON())) : '');
                    }

                    return (!self._checkItemExists(next_el.get('id')) ? prev_el.concat(ItemTemplate(_.defaults({'CLASS_ITEM': Settings.Gallery.el} ,next_el.toJSON()))) : prev_el);
                }));
                self.isLoading = false;
            },
            error: function(collection, response){
                self.isLoading = false;
            }, 
            at:this.itemsCollectionObj.length, remove: false});
        },
        showSingleItem: function(item){
            // Cargando vista de la carga singular 
            new Item({'item': item, 'itemList': this.itemsCollectionObj, 'gallery': this.galleryObj, 'ItemTemplate': ItemSingletemplate}).render();
        },
        _checkScroll: function(e) {
            if(!this.isLoading && !this.endRequests && document.body.scrollTop + document.body.clientHeight + this._triggerPoint > document.body.scrollHeight){
                this._loadItems();
            }
        },
        _checkItemExists: function(id){
            return ($("div.listItem[data-di='" + id + "']").length === 0 ? false : true);
        }
    });
});