!(function (root) {
    root.console || (root.console = {});
    typeof root.console.log !== 'function' && (root.console.log = function() {});
    if (typeof Function.prototype.bind === 'undefined') {
        Function.prototype.bind = function () {
            var fn = this, args = Array.prototype.slice.call(arguments), object = args.shift();
            return function () {
                return fn.apply(object,
                    args.concat(Array.prototype.slice.call(arguments)));
            };
        };
    }
    if (typeof root.addEventListener === 'undefined') {
        root.addEventListener = function (type, listener, useCapture) {
            return root.attachEvent('on' + type, listener);
        };
    }
    var require = root.require;
    require.config({
        baseUrl: '/static/js/',
        urlArgs: "refresh= " + (+new Date()), //"refresh=20151588911489", 
        paths: {
            'jquery': 'gallery/lib/jquery/jquery-1.11.1.min',
            'jquery.lockfixed': 'libs/jquery/jquery.lockfixed',
            'jquery-ui': 'gallery/lib/jquery/jquery-ui-1.11.2.custom/jquery-ui.min',
            'jquery.upload': 'gallery/lib/jquery/jquery.upload',
            'jquery.cookie' : 'libs/jquery/jquery.cookie',
            'jquery.bubblepopup': 'libs/jquery/jquery.bubblepopup',
            'jquery.autosize.min': 'libs/jquery/jquery.autosize.min',
            'canvas-to-blob': 'gallery/lib/canvas-to-blob/canvas-to-blob.min',
            // 'load-image.all': 'gallery/lib/load-image/load-image.all.min',
            'load-image-meta': 'gallery/lib/load-image/load-image-meta',
            'load-image': 'gallery/lib/load-image/load-image',
            'load-image-exif-map': 'gallery/lib/load-image/load-image-exif-map',
            'load-image-exif': 'gallery/lib/load-image/load-image-exif',
            'load-image-ios': 'gallery/lib/load-image/load-image-ios',
            'jquery.ui.widget': 'gallery/lib/jquery/jquery.ui.widget',
            'jquery.iframe-transport': 'gallery/lib/jquery/jquery.iframe-transport',
            'jquery.fileupload-process': 'gallery/lib/jquery/jquery.fileupload-process',
            'jquery.fileupload-image': 'gallery/lib/jquery/jquery.fileupload-image',
            'jquery.fileupload': 'gallery/lib/jquery/jquery.fileupload',
            'underscore': 'libs/underscore/underscore-min',
            'backbone': 'libs/backbone/backbone-min',
            'bootstrap': 'libs/bootstrap/bootstrap.min',
        },
        waitSeconds: 30,
        shim: {
            bootstrap: {
                deps: ["jquery"]
            },
            underscore: {
                exports: '_'
            },
            backbone: {
                deps: ["underscore", "jquery"],
                exports: "Backbone"
            }
        }
    });
    
    require(['jquery', 'underscore'], function ($, _) {
        // define('usuario', function() {
        //     return usuario;
        // });
        $.noConflict(), _.noConflict();
        $(document).ready(function () {
            require(["gallery/apps/admin"], function (App) {
                App.initialize();
            });
        });
    });
}(this));