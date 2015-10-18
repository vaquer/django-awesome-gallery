define(['jquery', 'underscore', 'backbone'], function ($, _, BB){
    return BB.View.extend({
        el: $('div.banner'),
        events: {
            'click .close': 'closeDiv'
        },
        initialize: function(){

        },
        render: function(){
            console.log('LoadB');
        },
        closeDiv: function(){
            this.$el.css({'display': 'none'});
        }
    });
});