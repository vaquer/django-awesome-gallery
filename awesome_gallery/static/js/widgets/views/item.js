define(['jquery', 'underscore', 'backbone', 'GalSettings', 'general_settings', 'gallery/widgets/models/item', 'hgn!gallery/templates/desktop/galleryRelated', 'gallery/widgets/views/singleFotoSwipe'], 
    function ($, _, BB, Settings, GeneralSettings, ItemModel, GalleryRelatedTemplate, singleFotoSwipe){
    return BB.View.extend({
        el: (GeneralSettings ? $('.' + GeneralSettings.el + 'float'): null),
        isFirefox: (navigator.userAgent.toLowerCase().indexOf('firefox') > -1 ? true : false),
        itemObj: null,
        doRender: true,
        related: false,
        boxCommentVisible: false,
        titleEmbed: null,
        swipeObjetc: null,
        dataObjects: {
            gallery: null,
            itemList: null,
            item: null,
            ItemTemplate: null,
            isEmbed: false,
            renderbyURL: false,
        },
        events: {
            'click .next': 'showNextItem',
            'click .prev': 'showPrevItem',
            'click .closer': 'closeSingleItem',
            'click .comentar-btn': 'openCommentsBox',
            'mouseover .arelated' : 'showFooter',
            'mouseout .arelated': 'hideFooter'
        },
        initialize: function(options){
            _.bindAll(this, 'showPrevItem', 'showNextItem', 'closeSingleItem', 'renderRutine', 'openCommentsBox', 'changeOrientationMobile', 'callbackSwipe');
            var model_search = null,
                self = this,
                sett = _.extend(Settings, GeneralSettings);

            this.dataObjects = _.defaults(options || {}, this.dataObjects);

            if(this.dataObjects.isEmbed){
                this.titleEmbed = $('h2.title').html();
                this.swipeObjetc = new singleFotoSwipe();
                if(GeneralSettings.IS_MOBILE){
                    this.swipeObjetc.callback = this.callbackSwipe;
                }
            }

            if(this.dataObjects.itemList){
                model_search = this.dataObjects.itemList.findWhere({'id': parseInt(this.dataObjects.item)});
                if(model_search === undefined){
                    this.doRender = false;
                    this.itemObj = new ItemModel({'id': this.dataObjects.item});
                    this.itemObj.fetch({
                        success: function(model, response){
                            self.itemObj = model;
                            self.doRender = true;
                            self.renderRutine(sett, false);
                        },
                        error: function(model, response){console.error(response);}});
                }else{
                    this.itemObj = new ItemModel(model_search.toJSON());
                }
            }else{
                if(typeof this.dataObjects.item === 'number'){
                    this.doRender = false;
                    this.itemObj = new ItemModel({'id': this.dataObjects.item});
                    this.itemObj.fetch({
                        success: function(model, response){
                            self.itemObj = model;
                            self.doRender = true;
                            self.renderRutine(sett, false);
                        },
                        error: function(model, response){console.error(response);}});
                }else{
                    this.itemObj = new ItemModel(this.dataObjects.item);
                }
            }

            if(GeneralSettings.IS_MOBILE){
                window.addEventListener('orientationchange', this.changeOrientationMobile);
            }
        },
        render: function(){
            var self = this;

            if(this.doRender){
                this.renderRutine(_.extend(Settings, GeneralSettings));
            }

            if(this.dataObjects.isEmbed && GeneralSettings.IS_MOBILE){
                this.swipeObjetc.render();
            }

            if(!GeneralSettings.IS_MOBILE){
                this.$el.css('display', 'block');
                this.$el.addClass('single_gallery_overlay');
            }

            $(document).keydown(function(e) {
                switch(e.which) {
                    case 27:
                        self.closeSingleItem();
                    break;
                    case 37: // left
                        self.showPrevItem();
                    break;

                    case 39: // right
                        self.showNextItem();
                    break;

                    default: return; // exit this handler for other keys
                }
                e.preventDefault(); // prevent the default action (scroll / move caret)
            });

            return this;
        },
        callbackSwipe: function(swipedir){
            $('.foto_single_header_loading').css('visibility', 'visible');
            return (swipedir === 'left' ? this.showNextItem() : this.showPrevItem());
        },
        openCommentsBox: function(el){
            if(this.boxCommentVisible){
                this.$el.find('div.commentContainer').hide(200);
                this.boxCommentVisible = false;
            }else{
                this.$el.find('div.commentContainer').show(200);
                this.boxCommentVisible = true;
                /* jshintignore: start */
                FB.XFBML.parse();
                /* jshintignore: end */
            }
            return false;
        },
        renderRutine: function(Settings, doTrack){
            if(this.dataObjects.isEmbed){
                if(!this.dataObjects.renderbyURL){
                    if(!this.itemObj.get('slug')){
                        return false;
                    }
                    window.history.pushState("string", this.titleEmbed + this.itemObj.get('name'), this.dataObjects.embedURI + 'picture/' + this.itemObj.get('slug'));
                }
                this.dataObjects.renderbyURL = false;
            }else{
                window.history.pushState("string", this.itemObj.get('name'), this.itemObj.get('permalink'));
            }

            if(doTrack){
                /* jshint ignore:start */
                _gaq.push(['_trackPageview']);
                /* jshint ignore:end */
            }

            if(GeneralSettings.IS_MOBILE){
                this.itemObj = this.resizeItem(this.itemObj);
            }else{
                // this.itemObj = this.resizeItem(this.itemObj, 670, 503);
                this.itemObj = this.resizeItem(this.itemObj, $( window ).width() - 190, $( window ).height() - 190);
            }

            if(this.itemObj.get('about') === undefined || this.itemObj.get('about') === null || this.itemObj.get('about') === 'undefined' || !this.itemObj.get('about')){
                this.itemObj.set({'about': false});
            }

            if(this.itemObj.get('height_new') > 400){
                this.itemObj.set({'width_facebook': this.itemObj.get('width_new') - 20});
            }

            this.itemObj.set({'width-container': 412 + this.itemObj.get('width_new')});

            this.$el.find('div.container').html(this.dataObjects.ItemTemplate(_.defaults({
                'FQDN': Settings.FQDN,
                'related_galeries_random': this.relatedGaleriesRandom(),
                'SocialUri': encodeURIComponent('http://' + GeneralSettings.BASE_FQDN + this.itemObj.get('permalink')),
                'banner_url': Settings.banner_url,
                'count_g': this.dataObjects.gallery.get('count'),
                'g_name': this.dataObjects.gallery.get('name'),
                'FACEBOOK_APP_ID': GeneralSettings.FACEBOOK_APP_ID,
                'BASE_FQDN': GeneralSettings.BASE_FQDN,
                'facebook_vertical': (this.itemObj.get('height') <= 400 ? true : false),
                'next': ((this.related && this.itemObj.get('next') !== null) || (!this.related && this.itemObj.get('next') === null) ? this.itemObj.get('id') : null),
                'prev': ((this.related && this.itemObj.get('prev') !== null) || (!this.related && this.itemObj.get('prev') === null) ? this.itemObj.get('id') : null)
                },this.itemObj.toJSON())));
            this.$el.css({'overflow': 'hidden'});
            $('.' + Settings.el + 'float').addClass('visible');
            $.ajax({ url: 'http://platform.twitter.com/widgets.js', dataType: 'script', cache:true});
            $.ajax({ url: 'https://apis.google.com/js/plusone.js', dataType: 'script', cache:true});
        },
        relatedGaleriesRandom: function(){
            var rnd = Math.floor(Math.random() * (this.dataObjects.gallery.get('related_galeries').objects.length - 1)) + 0;
            return this.dataObjects.gallery.get('related_galeries').objects[rnd];
        },
        showPrevItem: function(){
            var prevItem = undefined,
                self = this,
                sett = _.extend(Settings, GeneralSettings);

            if(this.dataObjects.itemList){
                prevItem = (this.itemObj.get('prev') ? this.dataObjects.itemList.findWhere({'order': (this.itemObj.get('order') - 1)}) : this.dataObjects.itemList.findWhere({'order': this.dataObjects.itemList.size()}));
            }

            this.related = false;
            if(prevItem === undefined){
                this.itemObj = new ItemModel({'id': parseInt(this.itemObj.get('prev'))});
                this.itemObj.fetch({
                    success: function(model, response){
                        self.itemObj = model;
                        self.doRender = true;
                        self.renderRutine(sett, false);
                    },
                    error: function(model, response){console.error(response);}});
            }else{
                this.itemObj = prevItem;
                this.renderRutine(_.extend(Settings, GeneralSettings), true);
            }
            if(this.dataObjects.isEmbed && GeneralSettings.IS_MOBILE){
                this.swipeObjetc.defineSwipeElement();
            }

            return false;
        },
        showNextItem: function(){
            var nextItem = undefined,
                self = this,
                sett = _.extend(Settings, GeneralSettings);

            if(this.dataObjects.itemList){
                nextItem = (this.itemObj.get('next') ? this.dataObjects.itemList.findWhere({'order': (this.itemObj.get('order') + 1)}) : this.dataObjects.itemList.findWhere({'order': 1}));
            }

            this.related = false;
            if(nextItem === undefined){
                this.itemObj = new ItemModel({'id': parseInt(this.itemObj.get('next'))});
                this.itemObj.fetch({
                    success: function(model, response){
                        self.itemObj = model;
                        self.doRender = true;
                        self.renderRutine(sett, false);
                    },
                    error: function(model, response){console.error(response);}});
            }else{
                this.itemObj = nextItem;
                this.renderRutine(_.extend(Settings, GeneralSettings), true);
            }
            if(this.dataObjects.isEmbed && GeneralSettings.IS_MOBILE){
                this.swipeObjetc.defineSwipeElement();
            }
            return false;
        },
        closeSingleItem: function(){
            if(this.dataObjects.isEmbed){
                window.history.pushState("string", this.titleEmbed, this.dataObjects.embedURI);
            }else{
                window.history.pushState("string", Settings.Gallery.name, Settings.Gallery.permalink);
            }

            this.$el.removeClass('visible');
            this.$el.find('.container').html('');

            if(!GeneralSettings.IS_MOBILE){
                this.$el.css('display', 'none');
                this.$el.removeClass('single_gallery_overlay');
            }

            // Destroy the object view
            this.unbind();
            this.undelegateEvents(); 
            // BB.View.prototype.remove.call(this);

            // Unbind events of the keyboard
            $(document).unbind("keydown", (function(e){ return; }));
        },
        showFooter: function(e){
            $(e.currentTarget).find('div.footrelated').css({'display': 'block'});
        },
        hideFooter: function(e){
            $(e.currentTarget).find('div.footrelated').css({'display': 'none'});
        },
        showRelated: function(direction){
            var context = null,
                template = GalleryRelatedTemplate,
                related_galeries = null;
            window.history.pushState("string", Settings.Gallery.name, Settings.Gallery.permalink + (direction === "next" ? '/related-galeries-end/' : '/related-galeries-init/'));
            if(this.dataObjects.gallery.get('related_galeries').objects.length > 1){
                related_galeries = _.reduce(this.dataObjects.gallery.get('related_galeries').objects, function(prev_el, next_el){
                    if(!_.isString(prev_el)){
                        prev_el = template(prev_el);
                    }
                    return prev_el.concat(template(next_el));
                });
            } else if(this.dataObjects.gallery.get('related_galeries').objects.length === 1){
                related_galeries = template(this.dataObjects.gallery.get('related_galeries').objects[0]);
            }

            context = _.defaults({
                'related_galeries': related_galeries,
                'g_name': this.dataObjects.gallery.get('name'),
                'prev': (direction === 'previus' ? null : this.itemObj.get('id')),
                'next': (direction === 'next' ? null : this.itemObj.get('id')),
                'related_url': true,
                'FQDN': GeneralSettings.FQDN,
                'FACEBOOK_APP_ID': GeneralSettings.FACEBOOK_APP_ID,
                'BASE_FQDN': GeneralSettings.BASE_FQDN,
                'facebook_vertical': (this.itemObj.get('height') < 350 ? true : false)
            }, this.itemObj.toJSON());
            this.$el.find('.container').html(this.dataObjects.ItemTemplate(context));
            this.related = true;
        },
        changeOrientationMobile: function(el){
            this.resizeItem(this.itemObj);
            this.$el.find('img.img_embed').css({'width': this.itemObj.get('width_new'), 'height': this.itemObj.get('height_new'), 'margin': this.itemObj.get('margin-top').toString() + 'px auto'});
        },
        resizeItem: function(item, widthCanva, heightCanva){
            var iOS = /iPad|iPhone|iPod/.test(navigator.platform),
                width = widthCanva || ((window.orientation === 90 || window.orientation === -90) && iOS ? screen.height - 20 : screen.width - 20),
                height = heightCanva || ((window.orientation === 90 || window.orientation === -90) && iOS ? screen.width - 20 : screen.height - 20),
                new_width = 0,
                new_height = 0,
                new_margin_top = 0,
                rw = 0,
                rh = 0,
                k = 0;

            if(item.get('is_video')){
                item.set({'width_new': 670, 'height_new': 500, 'margin-left': 0, 'margin-top': 0, 'vertical': false});
                new_width = 670;
                new_height = 500;
                new_margin_top = 0;
            }else{
                if(!item.get('vertical')){
                    if(item.get('width') <= width && item.get('height') <= height){
                        item.set({'width_new': item.get('width'), 'height_new': item.get('height'), 'margin-left': (width -  item.get('width') === 0 ? 0 : parseInt((width -  item.get('width'))/2)), 'margin-top': (height - item.get('height') === 0 ? 0 : parseInt((height - item.get('height'))/2) - 30)});
                        new_margin_top = (height - item.get('height') === 0 ? 0 : parseInt((height - item.get('height'))/2));
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

                        item.set({'width_new': new_width, 'height_new': new_height, 'margin-left': (width - new_width === 0 ? 0 : parseInt((width - new_width)/2)), 'margin-top': (height - new_height === 0 ? 0 : parseInt((height - new_height)/2)) - 30, 'vertical': false });
                        new_margin_top = (height - new_height === 0 ? 0 : parseInt((height - new_height)/2));
                    }
                    if(item.get('width') < item.get('height') || item.get('margin-top') < 0){
                        item.set('margin-top', item.get('margin-top') + 30);
                    }
                }else{
                    if(item.get('width') <= width && item.get('height') <= height){
                        item.set({'width_new': item.get('width'), 'height_new': item.get('height'), 'margin-left': (width -  item.get('width') === 0 ? 0 : parseInt((width -  item.get('width'))/2)), 'margin-top': (height - item.get('height') === 0 ? 0 : parseInt((height - item.get('height'))/2))});
                        new_margin_top = (height - item.get('height') === 0 ? 0 : parseInt((height - item.get('height'))/2));
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

                        item.set({'width_new': new_width, 'height_new': new_height, 'margin-left': (width - new_width === 0 ? 0 : parseInt((width - new_width)/2)), 'margin-top': (height - new_height === 0 ? 0 : parseInt((height - new_height)/2)), 'vertical': false });
                        new_margin_top = (height - new_height === 0 ? 0 : parseInt((height - new_height)/2));
                    }
                }
            }
            item.set({'width_border': (new_width > 0 ? new_width + 28 : item.get('width') + 28), 'height_border': new_height + 28, 'width_facebook': (new_width > 0 ? new_width / 2 : item.get('width') / 2), 'height_facebook': (new_height > 0 ? new_height / 2 : item.get('height') / 2) - 20, 'margin-top-borer': (new_margin_top > 40 ? new_margin_top : new_margin_top + 25)});
            return item;
        }
    });
});