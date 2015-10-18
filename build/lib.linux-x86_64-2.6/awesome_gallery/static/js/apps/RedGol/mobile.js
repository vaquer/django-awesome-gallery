define(function (require, exports, module) {
    var $ = require('jquery'),
        _ = require('underscore'),
        BB = require('backbone'),
        User = require('widgets/views/user'),
        FBView = require('widgets/views/rgfb'),
        Interfaz = require('widgets/views/interfaz'),
        ChooserTeam = require('widgets/views/chooserteam'),
        ShareMobile = require('widgets/views/shareMobile'),
        MetaGalleryJG = require('gallery/widgets/views/galleries'),
        SmartBanner = require('widgets/views/smartBanner'),
        View = BB.View.extend({
            UserModule: null,
            InterfazModule: null,
            FbModule: null,
            initialize: function (params) { 
                console.log("Inicilizando botonessociales-mobile.js");
                this.UserModule = new User();
                this.InterfazModule = new Interfaz();
                this.InterfazModule.userInfo = this.UserModule;
                this.FbModule = new FBView();
                this.FbModule.interfazID = this.InterfazModule;
            },
            render: function (site) {
                this.UserModule.render();
                this.InterfazModule.render();
                this.FbModule.render();
                new ChooserTeam().render();
                new ShareMobile().render();
                new MetaGalleryJG().render();
                new SmartBanner().render();
            }
        });
    BB = BB.noConflict();
    return {
        initialize: function (params) {
            new View(params || {}).render();
        }
    };
});
