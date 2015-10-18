define(['underscore', 'backbone', 'gallery/widgets/models/gallery'], function (_, BB, galleryModel){
    return BB.Collection.extend({
        model: galleryModel,
        _limit: 20,
        defaults: {
            next: null,
            offset: 20,
            previous: null,
            total_count: null
        },
        initialize: function(models, options){
            this.options = _.defaults(options || {}, this.defaults);
            this.reset(models);
        },
        parse: function(resp, xhr){
            this.options = _.defaults(resp.meta || {}, this.defaults);
            return resp.objects;
        },
        url: function(){
            if(!this.options.next){
                this.options.next = '/gallery/api/v1/gallery/?offset=40&limit=20';
                return '/gallery/api/v1/gallery/?offset=20&limit=20';
            }else{
                return this.options.next;                
            }
        }
    });
});