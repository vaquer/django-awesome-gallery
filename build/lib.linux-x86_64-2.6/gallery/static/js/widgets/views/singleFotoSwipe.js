/* jshint ignore:start */
define(['jquery','underscore','backbone'], function ($,_,BB){
    return BB.View.extend({
        el: $('#swipeft'),
        dataPic: null,
        events: { },
        callback: null,
        initialize: function() {
            _.bindAll(this, 'changeOrientationMobile');
        },
        swipeDetect: function (el,callback) {
            var touchsurface = el,
            swipedir,
            startX,
            startY,
            distX,
            distY,
            threshold = 50, //required min distance traveled to be considered swipe - estaba en 150
            restraint = 100, // maximum distance allowed at the same time in perpendicular direction
            allowedTime = 300, // maximum time allowed to travel that distance
            elapsedTime,
            startTime,
            handleswipe = callback || function(swipedir){}
            //
            touchsurface.addEventListener('touchstart', function(e){
                var touchobj = e.changedTouches[0];
                swipedir = 'none';
                dist = 0;
                startX = touchobj.pageX;
                startY = touchobj.pageY;
                startTime = new Date().getTime(); // record time when finger first makes contact with surface
                e.preventDefault();
            }, false)
            touchsurface.addEventListener('touchmove', function(e){
                e.preventDefault(); // prevent scrolling when inside DIV
            }, false)
            //
            touchsurface.addEventListener('touchend', function(e){
                var touchobj = e.changedTouches[0]
                distX = touchobj.pageX - startX; // get horizontal dist traveled by finger while in contact with surface
                distY = touchobj.pageY - startY; // get vertical dist traveled by finger while in contact with surface
                elapsedTime = new Date().getTime() - startTime; // get time elapsed
                if (elapsedTime <= allowedTime){ // first condition for awipe met
                    if (Math.abs(distX) >= threshold && Math.abs(distY) <= restraint){ // 2nd condition for horizontal swipe met
                        swipedir = (distX < 0)? 'left' : 'right'; // if dist traveled is negative, it indicates left swipe
                    }
                    else if (Math.abs(distY) >= threshold && Math.abs(distX) <= restraint){ // 2nd condition for vertical swipe met
                        swipedir = (distY < 0)? 'up' : 'down'; // if dist traveled is negative, it indicates up swipe
                    }
                }
                if(swipedir === 'left' || swipedir === 'right'){
                    handleswipe(swipedir);
                }
                e.preventDefault();
            }, false)
        },
        render: function(loadOrientationEvent) {
            if(loadOrientationEvent){
                window.addEventListener('orientationchange', this.changeOrientationMobile);
            }
            if($('.pic_mobile').length > 0){
                this.dataPic = JSON.parse(JSON.stringify(eval("(" + $('.pic_mobile').attr('data-pic') + ")")));
                $('.pic_mobile').css(_.extend({'display': 'inline-flex'}, this.resizeItemEmbed(parseInt($('.foto_single_contenedor').width() - 25), parseInt($('.foto_single_contenedor').height()) - 36, parseInt(this.dataPic.width), parseInt(this.dataPic.height))));
            }

            if(/iPad|iPhone|iPod/.test(navigator.platform)){
                $('.pic_mobile').css({'display': 'inline-block'});
            }
            this.defineSwipeElement();
        },
        defineSwipeElement: function(){
            this.el = this.$el = $('#swipeft')[0];
            this.callback = (!this.callback ? function(swipedir){
                $('.foto_single_header_loading').css("visibility","visible");
                return window.location = (swipedir === 'left' ? RGFoto.url_siguiente : RGFoto.url_anterior);
            } : this.callback);

            this.swipeDetect(this.el, this.callback);
        },
        changeOrientationMobile: function(el){
            var new_size = this.resizeItemEmbed(null, null, this.dataPic.width, this.dataPic.height);
            $('img.pic_mobile').css({'width': new_size.width, 'height': new_size.height, 'margin': new_size.margin_top + ' auto'});
        },
        resizeItemEmbed: function(widthCanva, heightCanva, widthImage, heightImage){
           var iOS = /iPad|iPhone|iPod/.test(navigator.platform),
                width = widthCanva || ((window.orientation === 90 || window.orientation === -90) && iOS ? screen.height - 20 : screen.width - 20),
                height = heightCanva || ((window.orientation === 90 || window.orientation === -90) && iOS ? screen.width - 20 : screen.height - 20),
                new_width = 0,
                new_height = 0,
                new_margin_top = 0,
                rw = 0,
                rh = 0,
                k = 0;


            if(widthImage <= width && heightImage <= height){
                return {'width': widthImage + 'px', 'height': heightImage + 'px', 'margin-top': (height - heightImage === 0 ? 0 : parseInt((height - heightImage)/2)) + 36 + 'px'};
            }else{
                rw = widthImage / width;
                rh = heightImage / height;
                
                if(rw > rh){
                    new_height = (width > widthImage ? parseInt(heightImage * rw) : parseInt(heightImage / rw));
                    new_width = width;
                }else{
                    new_width = (height > heightImage ? parseInt(widthImage * rh) : parseInt(widthImage / rh));
                    new_height = height;
                }

                return {'width': new_width + 'px', 'height': new_height + 'px', 'margin-top': (height - new_height === 0 ? 0 : parseInt((height - new_height)/2)) + 36 + 'px', 'margin_top': (parseInt($('.foto_single_contenedor').height()) - new_height === 0 ? 0 : parseInt((parseInt($('.foto_single_contenedor').height()) - new_height)/2)) + 10 + 'px', 'vertical': false };
            }
        }
    });
});
/* jshint ignore:end */