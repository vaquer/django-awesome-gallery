define(function (require, exports, module) {
    var $ = require('jquery'),
        _ = require('underscore'),
        BB = require('backbone'),
        //Settings = require('settings'),
        MetaGalleryJG = require('gallery/widgets/views/galleries'),
        Botones = require('widgets/views/compartir'),
        //PostsView = require('widgets/views/posts'),
        View = BB.View.extend({
            UserModule: null,
            InterfazModule: null,
            FbModule: null,
            initialize: function (params) { 
                console.log("Inicilizando botonessociales-mobile.js");
                //if(Settings.categoria) {
                    // Scroll infinito de posts solo cuando estamos mostrando el home, categoria o equipo
                    //this.Posts = new PostsView();
                //}
            },
            render: function (site) {
                new MetaGalleryJG().render();
                new Botones().render();
            }
        });
    BB = BB.noConflict();
    return {
        initialize: function (params) {
            new View(params || {}).render();
        }
    };
});
