define(function (require, exports, module) {
    var $ = require('jquery'),
        _ = require('underscore'),
        BB = require('backbone'),
        StickyBox = require('widgets/views/sticky_box'),
        Gallery = require('gallery/widgets/views/gallery'),
        User = require('widgets/views/user'),
        FBView = require('widgets/views/rgfb'),
        Interfaz = require('widgets/views/interfaz'),
        ChooserTeam = require('widgets/views/chooserteam'),
        ShareMobile = require('widgets/views/shareMobile'),
        View = BB.View.extend({
            UserModule: null,
            InterfazModule: null,
            FbModule: null,
            initialize: function (params) {
                this.UserModule = new User();
                this.InterfazModule = new Interfaz();
                this.InterfazModule.userInfo = this.UserModule;
                this.FbModule = new FBView();
                this.FbModule.interfazID = this.InterfazModule;
            },

            render: function (site) {
                // this parameter then we can access through view.options.candidatos or view.options.propuestas.
                new StickyBox().render();
                new Gallery().render();
                this.UserModule.render();
                this.InterfazModule.render();
                this.FbModule.render();
                new ChooserTeam().render();
                new ShareMobile().render();
            }
        });
    BB = BB.noConflict();

    return {
        initialize: function (params) {
            new View(params || {}).render();
        }
    };
});
