/* jshint ignore:start */
define(['jquery', 'underscore', 'backbone', 'utils', 'gallery/widgets/collections/galleries', 'hgn!gallery/templates/desktop/gallery'], 
    function ($, _, BB, Utils, GalleryCollectionClass, GalleryTemplate){
    return BB.View.extend({
        el: $('body'),
        _triggerPoint: 1500,
        isLoading: false,
        endRequests: false,
        _galleryCollection: null,
        events: { },
        initialize: function () { },
        render: function() {
            _.bindAll(this, '_checkScroll');
            this._galleryCollection = new GalleryCollectionClass();
            $(window).scroll(this._checkScroll);
            return this;
        },
        _loadGalleries: function(){
            var self = this;
            this.isLoading = true;
            this._galleryCollection.fetch({
                success: function(collection, response) {
                    //Nos aseguramos de detener las consultas
                    if(!collection.options.next){
                        self.endRequests = true;
                    }

                    $('#galleries').append(_.reduce(collection.models.slice(-20),
                        function(prev_el, next_el){
                            if(!_.isString(prev_el)){
                                prev_el = (!self._checkGalleryExists(next_el.get('id')) ? GalleryTemplate(prev_el.toJSON()) : '');
                            }

                            return (!self._checkGalleryExists(next_el.get('id')) ? prev_el.concat(GalleryTemplate(next_el.toJSON())) : prev_el);
                    }));
                    
                    $(".gallery_rg").css("display", "block");
                    self.isLoading = false;
                },
                error: function(collection, response) {
                    self.isLoading = false;
                },
                at: this._galleryCollection.length, remove: false
            });
        },
        _checkScroll: function(e) {
            if(!this.isLoading && !this.endRequests && document.body.scrollTop + document.body.clientHeight + this._triggerPoint > document.body.scrollHeight){
                this._loadGalleries();
            }
        },
        _checkGalleryExists: function(id){
            return ($("div.gallery_rg[data-di='" + id + "']").length === 0 ? false : true);
        }
    });
});
/* jshint ignore:end */