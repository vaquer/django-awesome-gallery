define(['jquery', 'underscore', 'backbone', 'gallery/widgets/views/embed'], 
    function ($, _, BB, EmbedView) {
        return BB.View.extend({
            elements: null,
            el: $('.gallery_embed'),
            initialize: function(){

            },
            render: function(){
                for(key=0; key < this.$el.length; key++){
                    new EmbedView({el: this.$el[key]}).render()
                }

               return this;
            }
        });
});