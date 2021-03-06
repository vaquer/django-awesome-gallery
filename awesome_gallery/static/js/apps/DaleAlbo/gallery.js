define(function (require, exports, module) {
    var $ = require('jquery'),
        _ = require('underscore'),
        BB = require('backbone'),
        StickyBox = require('widgets/views/sticky_box'),
        Gallery = require('gallery/widgets/views/gallery'),

        View = BB.View.extend({
            UserModule: null,
            InterfazModule: null,
            FbModule: null,
            initialize: function (params) {
               console.log('Init');
            },

            render: function (site) {
                // this parameter then we can access through view.options.candidatos or view.options.propuestas.
                new StickyBox().render();
                new Gallery().render();
            }
        });
    BB = BB.noConflict();

    return {
        initialize: function (params) {
            new View(params || {}).render();
        }
    };
});
