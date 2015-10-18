define(['jquery', 'underscore', 'backbone'], function ($, _, BB){
    return BB.Model.extend({
        defaults:{
            id: null,
            name: '',
            about: '',
            key_name: '',
            administrator: 0,
            order: 0,
            path: '',
            tags: '',
            hd: true,
            enabled: true,
            html: "",
            width_e: 0,
            height_e: 0,
            margin_left_e:0,
            margin_top_e: 0
        },
        url: function(){
            return '/gallery/api/v1/item/' + this.get('id') + '/?format=json';
        }
    });
});