define(function (require, exports, module) {
    var $ = require('jquery'),
        _ = require('underscore'),
        BB = require('backbone'),
        MetaGalleryJG = require('gallery/widgets/views/galleries'),
        View = BB.View.extend({
            UserModule: null,
            InterfazModule: null,
            FbModule: null,
            initialize: function (params) { 
                console.log("Inicilizando botonessociales-mobile.js");
            },
            render: function (site) {
                new MetaGalleryJG().render();
            }
        });
    BB = BB.noConflict();
    return {
        initialize: function (params) {
            new View(params || {}).render();
        }
    };
});
