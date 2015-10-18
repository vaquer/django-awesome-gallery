define(['jquery', 'underscore', 'backbone', 'gallery/widgets/models/item'], function ($, _, BB, Item){
    return BB.Collection.extend({
        model: Item,
        initialize: function(){

        }
    });
});