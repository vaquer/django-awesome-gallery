define(['jquery', 'underscore', 'backbone', 'general_settings', 'GalSettings', 'gallery/widgets/collections/items', 'gallery/widgets/models/gallery', 'gallery/widgets/views/item', 'hgn!gallery/templates/desktop/galleryItem', 'hgn!gallery/templates/desktop/item', 'hgn!gallery/templates/general/itemEmbed', 'hgn!gallery/templates/general/itemEmbedDetail', 'hgn!gallery/templates/mobile/embedItem'],
    function ($, _, BB, GeneralSettings, Settings, ItemColection, GalleryModel, ItemView, TemplateItemSmall, TemplateItemBDetail, TemplateItmEmbed, TemplateItmEmbedDetail, TemplateMobileEmbedItem) {
        return BB.View.extend({
            el: $('.gallery_embed'),
            slug: null,
            idGal: null,
            size: null,
            items: null,
            gallery: null,
            doRender: false,
            galleryLoad: false,
            donextPage: true,
            width: null,
            height: null,
            actualItem: null,
            firstItem: null,
            lastItem: null,
            currentURL: null,
            loadSingleItem: false,
            isExpanded: false,
            events: {
                'click li.full, .imgShow, .expand': 'showSingleItem',
                'click li.thumbs': 'expandGallery',
                'click .control_next': 'showNext',
                'click .control_prev': 'showPrev',
                'click .singleEmbed': 'showSingleItemDetail',
                'click .expand .slider-actions .mini': 'showMini',
                'click .nextLoad': 'loadNext'
            },
            initialize: function(){
                _.bindAll(this, 'showSingleItemFunc');
                // Configuracion del size de la vista
                this.width = this.$el.width();
                this.height = Math.round(this.width / 1.3);
                this.size = this.width + 'x' + this.height;
                // Propiedades de la vista 
                this.slug = this.$el.attr('data-slg');
                this.idGal = this.$el.attr('data-id');
                this.currentURL = GeneralSettings.ActualPermaLink;

                if(typeof GeneralSettings.IS_MOBILE === "string"){
                    GeneralSettings.IS_MOBILE = (GeneralSettings.IS_MOBILE === 'True' ? true : false);
                }

                // Inicializamos los modelos y colecciones
                if(Settings.ItemLoad){
                    if(Settings.ItemLoad.gallery.id === parseInt(this.idGal)){
                        this.gallery = new GalleryModel(Settings.ItemLoad.gallery);
                        this.galleryLoad = true;
                        this.loadSingleItem = true;
                    }else{
                        this.gallery = new GalleryModel({'slug': this.slug, 'id': this.idGal});
                    }
                }else{
                    this.gallery = new GalleryModel({'slug': this.slug, 'id': this.idGal});
                }

                this.gallery.url = '/gallery/api/v1/gallery/' + this.idGal + '/?format=json';

                if(this.loadSingleItem){
                    if(Settings.ItemLoad.item){
                        this.showSingleItemFunc(Settings.ItemLoad.item);
                    }
                }
                this.items = new ItemColection(null, {'gallery': this.slug});
            },
            render: function(){
                var self = this,
                    sett = Settings;

                this.$el.height(this.height);
                if(this.height < 350){
                    this.$el.find('.description').css('top', '93%');
                }
                
                if(!this.loadSingleItem){
                    this.gallery.fetch({success: function(model, response) {self.galleryLoad = true; _.extend(sett.Gallery, model.toJSON()); }, error: function(model, response){self.galleryLoad = false;}});
                }

                this.items.fetch({
                    success: function(collection, response) {
                        var that = self;
                        // Identificamos si existe una pagina siguiente
                        self.donextPage = (!collection.options.next ? false : true);
                        // Si ya hay algo en la colleccion simplemente se
                        if(collection.length > 0){
                            self.$el.find('ul.elements').append(_.reduce(collection.models.slice(-20), function (prev_el, next_el) {
                                if(!_.isString(prev_el)){
                                    prev_el = that.resizeItemEmbed(prev_el, that.width, that.height);
                                    prev_el = TemplateItmEmbed(prev_el.toJSON());
                                }
                                next_el = that.resizeItemEmbed(next_el, that.width, that.height);
                                return prev_el.concat(TemplateItmEmbed(next_el.toJSON()));
                            }));
                        }
                        //Activamos el proceso de rendereo
                        self.doRender = true;
                        // Seteamos las propiedades de la vista
                        self.actualItem = (collection.length > 0 ? collection.first().get('id') : null);
                        self.firstItem = self.actualItem;
                        self.lastItem = (collection.length > 0 ? collection.last().get('id') :  null);
                        // Hacemos visible la vista de detalle
                        self.$el.find('.load').css('display', 'none');
                        self.$el.find('.embed').css('display', 'block');
                        self.$el.find('.embed').animate({opacity: 1}, 200);
                        self.$el.find('.slider-actions').css('display', 'block');
                        // Vemos si decidimos mostrar una imagen
                        // if(self.loadSingleItem){
                        //     self.showSingleItemFunc(sett.ItemLoad.item.id);
                        // }
                    },
                    error: function(collection, response){
                        self.doRender = false;
                        self.$el.html($('</p>').addClass('error').text('Lo sentimos hemos experimentado un error.'));
                        console.log('Error gallery(' + self.slug + '): ' + response.error)
                    }, at:this.items.length, remove: false});

                return this;
            },
            showSingleItem: function(event){
                if(this.doRender && this.galleryLoad && !this.isExpanded && !$(event.target).hasClass('mini')){
                    this.showSingleItemFunc(this.actualItem);
                }
            },
            showSingleItemFunc: function(item){
                // Cargando vista de la carga singular 
                new ItemView({'item': item, 'itemList': this.items, 'gallery': this.gallery, 'ItemTemplate': (GeneralSettings.IS_MOBILE ? TemplateMobileEmbedItem : TemplateItemBDetail), 'isEmbed': true, 'embedURI': this.currentURL, 'renderbyURL': this.loadSingleItem}).render();
                this.loadSingleItem = false;
            },
            showNext: function(){
                var self = this;

                this.$el.find('ul.elements').animate({
                    left: - this.$el.find('ul.elements').width()
                }, 200, function () {
                    $('.gallery_embed[data-id=' + self.idGal + '] ul.elements li:first-child').appendTo('.gallery_embed[data-id=' + self.idGal + '] ul.elements');
                    $('.gallery_embed[data-id=' + self.idGal + '] ul.elements').css('left', '');
                    self.actualItem = $('.gallery_embed[data-id=' + self.idGal + '] ul.elements li:first-child').attr('data-itm');
                });

                if(this.doRender && this.galleryLoad){
                    this.showSingleItemFunc(this.actualItem);
                }
                return false;
            },
            showPrev: function(){
                var self = this;

                this.$el.find('ul.elements').animate({
                    left: + this.$el.find('ul.elements').width()
                }, 200, function () {
                    $('.gallery_embed[data-id=' + self.idGal + '] ul.elements li:last-child').prependTo('.gallery_embed[data-id=' + self.idGal + '] ul.elements');
                    $('.gallery_embed[data-id=' + self.idGal + '] ul.elements').css('left', '');
                    self.actualItem = $('.gallery_embed[data-id=' + self.idGal + '] ul.elements li:first-child').attr('data-itm');
                });

                if(this.doRender && this.galleryLoad){
                    this.showSingleItemFunc(this.actualItem);
                }
                return false;
            },
            showSingleItemDetail: function(event){
                if(this.doRender && this.galleryLoad){
                    this.showSingleItemFunc($(event.target).parent('a').attr('data-id'));
                }
                return false;
            },
            expandGallery: function(event){
                var self = this;
                this.isExpanded = true;
                this.$el.css({'height': '100%'});
                this.$el.find('.expand').animate({opacity: 1}, 200);

                if(!this.$el.find('.expand .contentEmbed').html()){
                    this.$el.find('.expand .contentEmbed').append(_.reduce(this.items.models.slice(-20), function (prev_el, next_el) {
                        if(!_.isString(prev_el)){
                            prev_el = TemplateItmEmbedDetail(prev_el.toJSON());
                        }
                        return prev_el.concat(TemplateItmEmbedDetail(next_el.toJSON()));
                    }));
                }
                //Activamos las galerias que no esten rendereadas
                this.$el.find('.expand .contentEmbed').justifiedGallery({sizeRangeSuffixes : {
                    'lt100': '', 
                    'lt240': '', 
                    'lt320': '', 
                    'lt500': '', 
                    'lt640': '', 
                    'lt1024': ''
                }});

                this.$el.find('.embed').animate({opacity: 0}, (GeneralSettings.IS_MOBILE ? 500 : 250), function(){self.$el.find('.embed').css('display', 'none');});

                if(!this.items.options.next){
                    this.$el.find('.nextLoad').css('display', 'none');
                }
            },
            showMini: function(){
                this.$el.find('.embed').css('display', 'block');
                this.$el.find('.expand').animate({opacity: 0}, 100);
                this.$el.animate({height: this.height}, 200);
                this.$el.find('.embed').animate({opacity: 1}, 200);
                this.isExpanded = false;
            },
            loadNext: function(){
                var self = this;

                if(this.items.options.next){
                    this.items.fetch({
                    success: function(collection, response){
                        self.donextPage = collection.options.next ? true : false;
                        self.$el.find('.expand .contentEmbed').append(_.reduce(collection.models.slice(-1 * response.objects.length),
                            function (prev_el, next_el){
                                if(!_.isString(prev_el)){
                                    prev_el = TemplateItmEmbedDetail(prev_el.toJSON());
                                }
                                return prev_el.concat(TemplateItmEmbedDetail(next_el.toJSON()));
                            })
                        );

                        // Volvemos a calcular el grid de imagenes
                        // self.$el.height((self.$el.find('.expand .content').height() * 2));
                        self.$el.find('.expand .contentEmbed').justifiedGallery({sizeRangeSuffixes : {
                            'lt100': '',
                            'lt240': '',
                            'lt320': '',
                            'lt500': '',
                            'lt640': '',
                            'lt1024': ''
                        }});

                        // Si ya no existen mas paginas impedimos que se realicen
                        if(!self.donextPage){
                            self.$el.find('.nextLoad').css('display', 'none');
                        }
                    },
                    error: function(collection, response){
                        self.$el.find('.nextLoad').css('display', 'none');
                    }
                    ,at:this.items.length, remove: false});
                }
            },
            resizeItemEmbed: function(item, widthCanva, heightCanva){
                var width = widthCanva,
                    height = heightCanva,
                    new_width = 0,
                    new_height = 0,
                    rw = 0,
                    rh = 0,
                    k = 0;

                if(item.get('is_video')){
                    item.set({'width_e': width, 'height_e': height, 'margin_left_e': 0, 'margin_top_e': 0, 'vertical': false});
                }else{
                    if(!item.get('vertical')){
                        if(item.get('width') <= width && item.get('height') <= height){
                            item.set({'width_e': item.get('width'), 'height_e': item.get('height'), 'margin_left_e': (width -  item.get('width') === 0 ? 0 : parseInt((width -  item.get('width'))/2)), 'margin_top_e': (height - item.get('height') === 0 ? 0 : parseInt((height - item.get('height'))/2))});
                        }else{
                            rw = item.get('width') / width;
                            rh = item.get('height') / height;
                            
                            if(rw > rh){
                                new_height = (width > item.get('width') ? parseInt(item.get('height') * rw) : parseInt(item.get('height') / rw));
                                new_width = width;
                            }else{
                                new_width = (height > item.get('height') ? parseInt(item.get('width') * rh) : parseInt(item.get('width') / rh));
                                new_height = height;
                            }

                            item.set({'width_e': new_width, 'height_e': new_height, 'margin_left_e': (width - new_width === 0 ? 0 : parseInt((width - new_width)/2)), 'margin_top_e': (height - new_height === 0 ? 0 : parseInt((height - new_height)/2)), 'vertical': false });
                        }
                    }else{
                        if(item.get('width') <= width && item.get('height') <= height){
                            item.set({'width_e': item.get('width'), 'height_e': item.get('height'), 'margin_left_e': (width -  item.get('width') === 0 ? 0 : parseInt((width -  item.get('width'))/2)), 'margin_top_e': (height - item.get('height') === 0 ? 0 : parseInt((height - item.get('height'))/2))});
                        }else{
                            rw = item.get('width') / width;
                            rh = item.get('height') / height;
                            
                            if(rw > rh){
                                new_height = (width > item.get('width') ? parseInt(item.get('height') * rw) : parseInt(item.get('height') / rw));
                                new_width = width;
                            }else{
                                new_width = (height > item.get('height') ? parseInt(item.get('width') * rh) : parseInt(item.get('width') / rh));
                                new_height = height;
                            }

                            item.set({'width_e': new_width, 'height_e': new_height, 'margin_left_e': (width - new_width === 0 ? 0 : parseInt((width - new_width)/2)), 'margin_top_e': (height - new_height === 0 ? 0 : parseInt((height - new_height)/2)), 'vertical': false });
                        }
                    }
                }

                return item;
            }
        });
});