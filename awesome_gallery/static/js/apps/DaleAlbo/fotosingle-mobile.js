define(function (require, exports, module) {
    var $ = require('jquery'),
        _ = require('underscore'),
        BB = require('backbone'),
        SingleFotoSwipe = require('gallery/widgets/views/singleFotoSwipe'),
        BannerControl = require('gallery/widgets/views/bannerMobile')
        View = BB.View.extend({
            initialize: function (params) { },
            render: function (site) {
                new SingleFotoSwipe().render();
                new BannerControl().render();
            }
        });
    BB = BB.noConflict();
    return {
        initialize: function (params) {
            new View(params || {}).render();
        }
    };
});
