define(['jquery', 'underscore', 'backbone', 'gallery/widgets/models/item'], function ($, _, BB, Item){
    return BB.Collection.extend({
        model: Item,
        defaults: {
            gallery: null,
            next: null,
            offset: 20,
            previous: null,
            total_count: null
        },
        initialize: function(models, options){
            this.options = _.defaults(options || {}, this.options);
            if(models){
                this.reset(models);
            }
        },
        parse: function(resp, xhr){
            this.options = _.extend(this.options, resp.meta || {});
            return resp.objects;
        },
        url: function(){
            if(!this.options.next){
                this.options.next = '/gallery/api/v1/item/?gallery__slug=' + this.options.gallery + '&offset=' + this.options.offset + '&limit=20&format=json';
                return '/gallery/api/v1/item/?gallery__slug=' + this.options.gallery + '&offset=0&limit=20&format=json';
            }

            return this.options.next;
        }
    });
});