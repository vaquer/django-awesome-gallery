define(function (require, exports, module) {
    var $ = require('jquery'),
        _ = require('underscore'),
        BB = require('backbone'),
        Admin = require('gallery/widgets/views/admin'),

        View = BB.View.extend({
            UserModule: null,
            InterfazModule: null,
            FbModule: null,
            // GalleryModule: null,
            initialize: function (params) {
                this.algo = 'something';
            },
            render: function (site) {
                new Admin().render();
            }
        });
    BB = BB.noConflict();

    return {
        initialize: function (params) {
            new View(params || {}).render();
        }
    };
});