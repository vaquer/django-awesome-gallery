define(['jquery', 'underscore', 'backbone', 'GallSettings',
    'load-image',
    'load-image-meta',
    'load-image-exif',
    'load-image-ios',
    'canvas-to-blob',
    'jquery.fileupload-process', 'jquery-ui', 'jquery.fileupload', 'jquery.fileupload-image'], 
    function ($, _, BB, Settings) {
    return BB.View.extend({
        el: $('#gallery_widget'),
        tag: 'div',
        nextorder: 0,
        currentOrder: 0,
        currentUpload: 0,
        uploads: 0,
        currentModelUpdate: null,
        actual: 0,
        dropable: false,
        multiselect: false,
        preOrder: null,
        changeOrder: false,
        isVideo: false,
        csrftoken: null,
        events:{
            'click .item-gallery': 'clickImage',
            'submit #form-item': 'submitEvent',
            'click #id_submit_video': 'submitVideo',
            'click #id_order_asc,#id_order_desc': 'setAutoOrder',
            'click .span_view_video': 'activateVideo',
            'click #id_order_cancelar,#id_auto_cancelar': 'cancelOrder',
            'click #id_order_manual': 'setOrderManual',
            'click #id_order_auto': 'autoOrderFunction',
            'click #id_select_multi': 'multiselectFunction',
            'click .delete_item': 'deleteItems',
            'click #id_enabled_btn': 'enabledItem',
            'click #id_disabled': 'disabledItem',
            'click .edit_link': 'doubleClickImageOpenDescript',
            'click #box_edit_form .close': 'closeUpdateBox',
            'click .btn-success': 'sendModificationRequest'
        },
        initialize: function(){
            this.getCookie();
        },
        render: function(){
            var self = this;

            function csrfSafeMethod(method) {
                // these HTTP methods do not require CSRF protection
                return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
            }
            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", self.csrftoken);
                    }
                }
            });
            
            this.nextorder = this.$el.find('ul.row_gallery').find('li.item-gallery').length;
            this.currentOrder = this.nextorder;
            this.fileManager();


        },
        getCookie: function (name) {
            var cookieValue = null;
            if (document.cookie && document.cookie != '') {
                var cookies = document.cookie.split(';');
                for (var i = 0; i < cookies.length; i++) {
                    var cookie = jQuery.trim(cookies[i]);
                    // Does this cookie string begin with the name we want?
                    if (cookie.substring(0, name.length + 1) == (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            this.csrftoken = cookieValue;
        },
        clickImage: function(e){
            $('.messages').removeClass('ok_request').removeClass('error_request');

            if(!this.dropable && !this.changeOrder){
                this.$el.find('ul.row_gallery').find('li.item-gallery').find('div.edit_zone').css({'display': 'none'});
                this.$el.find('ul.row_gallery').find('li.item-gallery').find('span.span_view_video').css({'display': 'none'});
                this.$el.find('ul.row_gallery').find('li.item-gallery').find('img').css({'margin-top': '0px'});
                this.$el.find('ul.row_gallery').find('li.item-gallery').find('div.video_preview').css({'margin-top': '0px'});
                this.$el.find('ul.row_gallery').find('li.item-gallery').find('div.video_preview').find('iframe').not($(e.currentTarget).find('iframe')).css({'width': '198px', 'height': '140px'});
                this.$el.find('ul.row_gallery').find('li.item-gallery').find('div.video_preview').not($(e.currentTarget).find('div.video_preview')).css({'max-height': '140px'});

                if(!this.multiselect){
                    this.$el.find('ul.row_gallery').find('li.item-gallery').removeClass("select");
                    $(e.currentTarget).find('div.edit_zone').css({'display': 'block'});
                    $(e.currentTarget).find('img').css({"margin-top": "-20px"});
                    if($(e.currentTarget).attr('data-video') === "True"){
                        $(e.currentTarget).find('span.span_view_video').css({'display': 'flex', 'margin-top': '-50px'});
                        $(e.currentTarget).find('div.video_preview').css({'margin-top': '-20px'});
                        $(e.currentTarget).find('iframe').css({'width': '193px', 'height': '133px'});
                        $(e.currentTarget).find('div.video_preview').css({'max-height': '133px'});
                    }
                }else{
                    $(e.currentTarget).find('img').css({"margin-top": "0px"});
                }
                $(e.currentTarget).addClass("select");
            }
        },
        doubleClickImageOpenDescript: function(el){
            var self = this;
            self.$el.find('#box_edit_form .modal-title').html('Item #' + $(el.currentTarget).parents('li.item-gallery').attr('data-order'));
            self.$el.find('#box_edit_form').show(200);
            $.get('/gallery/api/v1/item/' + $(el.currentTarget).parents('li.item-gallery').attr('data-id'))
                .done(function(response){
                    if(!response.error){
                        self.currentModelUpdate = response;

                        self.$el.find('#box_edit_form #descript_item_updt').val(response.about);
                        self.$el.find('#box_edit_form #edit_all').attr('href', '/masters-of-the-universe/gallery/item/' + response.id + '/');
                        self.$el.find('#box_edit_form .loadgin').hide(50);
                        self.$el.find('#box_edit_form .forms').show(200);
                    }
            });
            return false;
        },
        closeUpdateBox: function(){
            this.$el.find('#box_edit_form .feedback').html('');
            this.$el.find('#box_edit_form .loadgin').show(50);
            this.$el.find('#box_edit_form .forms').hide(50);
            this.$el.find('#box_edit_form').hide(200);
        },
        validateUpdatingBox: function(){
            this.$el.find('#box_edit_form .forms #descript_item_updt').attr('value', this.$el.find('#box_edit_form .forms #descript_item_updt').val());

            if(message.trim()){
                this.$el.find('#box_edit_form .feedback').html($('</p>').addClass('error').html(message));
            }
            return message.trim() ? false : true;
        },
        sendModificationRequest: function(el){
            var self = this,
                queryString = "item_id=" + this.currentModelUpdate.id + '&descript_item_updt=' + encodeURIComponent(escape(this.$el.find('#box_edit_form .forms #descript_item_updt').val()));

            $.post('/gallery/admin/add/description/key/', queryString)
                .done(function(response){
                    if(response.error){
                        self.$el.find('#box_edit_form .feedback').html($('<p>').addClass('error_request').css({'margin': '5px 0', 'text-align': 'center'}).html(response.error));
                        return false;
                    }

                    self.$el.find('#box_edit_form .feedback').html($('<p>').addClass('ok_request').css({'margin': '5px 0', 'text-align': 'center'}).html('Se ha modificado con exito.'));
                })
                .fail(function(response){
                    self.$el.find('#box_edit_form .feedback').html($('<p>').addClass('error_request').css({'margin': '5px 0', 'text-align': 'center'}).html('Ha habido un error'));
            });
        },
        activateVideo: function(e){
            $(e.currentTarget).siblings('img').css({'display': 'none'});
            $(e.currentTarget).siblings('div.video_preview').css({'display': 'flex', 'margin-top': '-20px'});
            $(e.currentTarget).css({'display': 'none'});
            e.preventDefault();
            return false;
        },
        enabledItem:function(e){
            $('.messages').removeClass('ok_request').removeClass('error_request');
            var ids_items = [],
                array_items = [];

            //Check if the select contains disabled items
            if(this.$el.find('ul.row_gallery').find('li.item-gallery.not-enabled-item.select').length > 0){
                //Get all the disabeld id's items
                _.each(this.$el.find('ul.row_gallery').find('li.item-gallery.not-enabled-item.select'), function(li){
                    ids_items.push($(li).attr('data-id').toString());
                    array_items.push(li);
                });

                //Send request to enabled items
                $.post('/gallery/admin/item/status/true/', {list_items: ids_items.join()})
                    .done(function(response){
                        if(!response.error){
                            _.each(array_items, function(li){
                                $(li).removeClass('not-enabled-item');
                            });
                            $('.messages').removeClass("error_request").addClass("ok_request").html('<p>Se ha realizado correctamente.</p>');
                        } else {
                            $('.messages').removeClass("ok_request").addClass("error_request").html('<p>Lo sentimos, ha ocurrido un error al intentar borrar los items.</p>');
                        }
                    })
                    .fail(function(response){
                        $('.messages').removeClass("ok_request").addClass("error_request").html('<p>Lo sentimos, ha ocurrido un error al intentar borrar los items.</p>');
                    }
                );
            }
        },
        disabledItem: function(e){
            $('.messages').removeClass('ok_request').removeClass('error_request');
            var ids_items = [],
                array_items = [];

            //Check if the select contains enabled items
            if(this.$el.find('ul.row_gallery').find('li.item-gallery.select').not(this.$el.find('ul.row_gallery').find('li.item-gallery.not-enabled-item.select')).length > 0){
                //Get all the enabeld id's items
                _.each(this.$el.find('ul.row_gallery').find('li.item-gallery.select').not(this.$el.find('ul.row_gallery').find('li.item-gallery.not-enabled-item.select')), function(li){
                    ids_items.push($(li).attr('data-id').toString());
                    array_items.push(li);
                });

                //Send request to disabled items
                $.post('/gallery/admin/item/status/false/', {list_items: ids_items.join()})
                    .done(function(response){
                        if(!response.error){
                            _.each(array_items, function(li){
                                $(li).addClass('not-enabled-item');
                            });
                            $('.messages').removeClass("error_request").addClass("ok_request").html('<p>Se ha realizado correctamente.</p>');
                        } else {
                            $('.messages').removeClass("ok_request").addClass("error_request").html('<p>Lo sentimos, ha ocurrido un error al intentar borrar los items.</p>');
                        }
                    })
                    .fail(function(response){
                        $('.messages').removeClass("ok_request").addClass("error_request").html('<p>Lo sentimos, ha ocurrido un error al intentar borrar los items.</p>');
                    }
                );
            }
        },
        deleteItems: function(e){
            $('.messages').removeClass('ok_request').removeClass('error_request');
            if(!$(e.currentTarget).prop("disabled")){
                var ids = [],
                    self = this,
                    count_elements = this.$el.find('ul.row_gallery').find('li.item-gallery.select').length,
                    deleted_elements = [];

                if(count_elements > 0){
                    //Se recuperan los seleccionados
                    _.each(this.$el.find('ul.row_gallery').find('li.item-gallery.select'), function(li){
                        ids.push($(li).attr("data-id").toString());
                        deleted_elements.push(li);
                    });

                    $.post('/gallery/admin/delete/key/', {id_list: ids.join()})
                        .done(function(data) {
                            if(!data.error){
                                self.preOrder = null;
                                self.nextorder -= count_elements;
                                _.each(deleted_elements, function(li){
                                    $(li).delete();
                                });
                                $('.messages').removeClass("error_request").addClass("ok_request").html('<p>Se ha realizado correctamente.</p>');
                            } else {
                                $('.messages').removeClass("ok_request").addClass("error_request").html('<p>Lo sentimos, ha ocurrido un error al intentar borrar los items.</p>');
                            }

                        })
                        .fail(function(data) {
                            $('.messages').removeClass("ok_request").addClass("error_request").html('<p>Lo sentimos, ha ocurrido un error al intentar borrar los items.</p>');
                    });
                }
            }
        },
        multiselectFunction: function(e){
            $('.messages').removeClass('ok_request').removeClass('error_request');
            if(!$(e.currentTarget).prop("disabled")){
                //Si no tenemos ningun item
                if(this.currentOrder === 0){
                    return false;
                }
                this.$el.find('ul.row_gallery').find('li.item-gallery').find('div.edit_zone').css({'display': 'none'});
                this.$el.find('ul.row_gallery').find('li.item-gallery').find('img').css({'margin-top': '0px'});
                this.multiselect = !this.multiselect ? true : false;
                if(!this.multiselect){
                    this.$el.find('ul.row_gallery').find('li.item-gallery').removeClass("select");
                }

                this.$el.find('.controls .other_tasks button').not($(e.currentTarget)).not($('#id_delete')).not($('#id_enabled_btn')).not($('#id_disabled')).prop("disabled", this.multiselect);
            }
        },
        setAutoOrder: function(e){
            if(!$(e.currentTarget).prop("disabled")){
                var _currentOrder = [],
                    self = this,
                    html = '';

                //Sentido de ordenamiento
                this.reverse = $(e.currentTarget).attr('id') === 'id_order_asc' ? false : true;
                //Obtenemos los ids
                _.each(this.preOrder, function(li){
                    _currentOrder.push(parseInt($(li).attr('data-id'), 10));
                });
                //Aplicamos el ordenamiento
                _currentOrder.sort(function(a, b){return self.reverse ? b-a : a-b;});

                _.each(_currentOrder, function(id){
                    html += $('<div>').append(self.$el.find('ul.row_gallery').find('li.item-gallery[data-id=' + id + ']').clone()).html();
                });

                //Preview del ordenamiento
                this.$el.find('ul.row_gallery').find('li.item-gallery').remove();
                this.$el.find('ul.row_gallery').prepend(html);
            }
        },
        autoOrderFunction: function(e){
            $('.messages').removeClass('ok_request').removeClass('error_request');
            if(!$(e.currentTarget).prop("disabled")){
                this.changeOrder = this.changeOrder ? false : true;
                if(this.changeOrder){
                    //Activamos el estado para confirmar los cambios
                    $(e.currentTarget).text("Confirmar");
                    $("#id_order_asc").css({'display': 'inline'});
                    $("#id_order_desc").css({'display': 'inline'});
                    $("#id_auto_cancelar").css({'display': 'inline'});
                    //Activamos el estado de botones
                    this.$el.find('.controls .other_tasks button')
                    .not($(e.currentTarget))
                    .not($("#id_order_cancelar"))
                    .not($("#id_auto_cancelar"))
                    .not($("#id_order_asc"))
                    .not($("#id_order_desc")).prop("disabled", true);

                    $("#id_auto_cancelar").prop("disabled", false);

                    //Obtenemos el orden previo
                    this.preOrder = this.$el.find('ul.row_gallery').find('li.item-gallery');
                } else {
                    //Volvemos a estado inicial
                    $(e.currentTarget).text("Automatico");
                    $("#id_order_asc").css({'display': 'none'});
                    $("#id_order_desc").css({'display': 'none'});
                    $("#id_auto_cancelar").css({'display': 'none'});
                    $("#id_auto_cancelar").css({'display': 'none'});
                    //Botones a estado inicial
                    this.$el.find('.controls .other_tasks button')
                    .not($(e.currentTarget))
                    .not($("#id_order_cancelar"))
                    .not($("#id_auto_cancelar"))
                    .not($("#id_order_asc"))
                    .not($("#id_order_desc")).prop("disabled", false);
                    //Confirmamos el orden actual
                    this.confirmReoirder();
                }
            }
        },
        setOrderManual: function(e){
            $('.messages').removeClass('ok_request').removeClass('error_request');
            if(!$(e.currentTarget).prop("disabled")){
                //Si no tenemos ningun item
                if(this.currentOrder === 0){
                    return false;
                }

                this.dropable = !this.dropable ? true : false;
                this.$el.find('.controls .other_tasks button').not($(e.currentTarget)).not($("#id_order_cancelar")).prop("disabled", this.dropable);
                //Ejecutar rutina de ordenado manual
                if(this.dropable){
                    //Habilitando sortable
                    this.$el.find('ul.row_gallery').find('li.item-gallery').removeClass("select");
                    $('.connectedSortable').sortable({ items: "li:not(.ui-state-disabled)"}).disableSelection();
                    //Cambios de interface
                    $(e.currentTarget).text("Confirmar");
                    this.$el.find('ul.row_gallery').find('li.item-gallery').removeClass("ui-state-disabled");
                    //Salvando orden previo
                    this.preOrder = this.$el.find('ul.row_gallery').find('li.item-gallery');
                    $("#id_order_cancelar").css({"display": "inline"});
                } else {
                    this.confirmReoirder();
                    $('.connectedSortable').sortable("destroy");
                    $(e.currentTarget).text("Manual");
                    $("#id_order_cancelar").css({"display": "none"});
                    this.$el.find('ul.row_gallery').find('li.item-gallery').addClass("ui-state-disabled");
                }
            }
        },
        confirmReoirder: function(){
            var current_order = '',
                self = this;

            //Obtenemos el orden actual
            _.each($(this.$el.find('ul.row_gallery').find('li.item-gallery')), function(li){
                if(current_order !== ''){
                    current_order += ',';
                }
                current_order += $(li).attr("data-id").toString();
            });

            // Reordering en el servidor
            $.post('/gallery/admin/reorder/', {id_list: current_order})
                .done(function(data){
                    $('.messages').removeClass("error_request").addClass("ok_request").html('<p>Se ha realizado correctamente.</p>');
                    self.changeOrder = false;
                })
                .fail(function(data){
                    $('.messages').removeClass("ok_request").addClass("error_request").html('<p>Lo sentimos. Ha ocurrido un error al intentar reordenar los items.</p>');
                    self.$el.find('ul.row_gallery').html();
                    self.$el.find('ul.row_gallery').fadeIn().html(self.preOrder);
                    self.preOrder = null;
                    self.changeOrder = false;
                });
        },
        cancelOrder: function(e){
            //Cancelacion del ordenado manual
            if(this.dropable || this.changeOrder){
                //Habilitamos los demas botones
                if(this.changeOrder){
                    $("#id_order_auto").text("Automatico");
                    $("#id_order_asc").css({'display': 'none'});
                    $("#id_order_desc").css({'display': 'none'});
                    $("#id_auto_cancelar").css({'display': 'none'});
                    $("#id_auto_cancelar").css({'display': 'none'});
                }

                if(this.dropable){
                    $("#id_order_manual").text("Manual");
                }

                $(e.currentTarget).css({"display": "none"});
                this.$el.find('.controls .other_tasks button').not($(e.currentTarget)).not($("#id_order_cancelar")).not($("#id_auto_cancelar")).prop("disabled", false);
                //Devolvemos el orden previo de los items
                this.$el.find('ul.row_gallery').find('li.item-gallery').remove();
                this.$el.find('ul.row_gallery').fadeIn().prepend(this.preOrder);
                //Estados default del objecto Backbone
                this.preOrder = null;
                this.dropable = false;
                this.changeOrder = false;
            }
        },
        confirmItem: function(item, video){
            this.addItemsval(item.id);
            //Agregamos el li como un item actualmente en el servidor
            this.$el.find('.row_gallery li.item-gallery[data-order=' + item.order + ']').attr({"data-id": item.id, "data-key": item.key_name});
            this.$el.find('.row_gallery li.item-gallery[data-order=' + item.order + ']').find('div.load_file_img').css({"display": "none"});
            this.$el.find('.row_gallery li.item-gallery[data-order=' + item.order + ']').find('div.load_file_img_bar').css({"display": "none"});
            //Agregamos el preview del video si es que existe
            if(video){
                this.$el.find('.row_gallery li.item-gallery[data-order=' + item.order + ']').find('img').remove();
                this.$el.find('.row_gallery li.item-gallery[data-order=' + item.order + ']').prepend(item.html);
                this.$el.find('.row_gallery li.item-gallery[data-order=' + item.order + ']').prepend($('<span/>').addClass('span_view_video'));
                this.$el.find('.row_gallery li.item-gallery[data-order=' + item.order + ']').append($('<div/>').addClass('video_preview').html(item.video));
            }
            this.$el.find('.row_gallery li.item-gallery[data-order=' + item.order + ']').find('img').css({"margin-top": "0"});
            this.$el.find('.row_gallery li.item-gallery[data-order=' + item.order + ']').prepend('<div class="edit_zone"><a href="' + item.admin + '" target="_blank"><span class="edit_icon"></span></a></div>');
        },
        addItemsval: function(val){
            //Agregamos el valor al input que controla los nuevos agregados
            var input = this.$el.find("#images"),
                value = input.val();

            if(value === ""){
                input.val(val);
            }else{
                input.val(value + ',' + val);
            }
        },
        changeProgess: function(order, progress){
            //Muestra el progreso de una imagen subida
            this.$el.find('.row_gallery li.item-gallery[data-order=' + order + ']').find('div.load_file_img').html("<p>" + progress + "%</p>");
            this.$el.find('.row_gallery li.item-gallery[data-order=' + order + ']').find('div.load_file_img_bar').css({"width": progress + '%'});
        },
        deletePreview: function(order){
            //Elimina el preview de una imagen subida fallida
            this.$el.find('.row_gallery li.item-gallery[data-order=' + order + ']').remove();
        },
        addCanvaImage: function(file, nextorder){
            //Agregamos un preview de una imagen subida
            if(typeof nextorder === 'number' && file.name !== ''){
                var ul = this.$el.find('.row_gallery'),
                    li = null,
                    preview = null,
                    self = this;

                if(!ul){
                    ul = $('<ul/>').attr({"id": "row-gallery"}).addClass("connectedSortable").addClass("row_gallery").addClass("ui-sortable");
                }

                li = $("<li/>").attr({"data-id": "", "data-parent": this.parent_id, "data-key": "", "data-order": nextorder}).addClass("item-gallery").addClass("ui-sortable-handle");

                li.append($("<div/>").addClass("load_file_img"));
                li.append($("<div/>").addClass("load_file_img_bar"));
                window.loadImage(
                    file,
                    function (img) {
                        if (img.src) {
                            $(img).attr({"width": "200px", "height": "140px"}).css({"margin-top": "-176px"});
                            li.append(img);
                        }
                    },{minWidth: 200, minHeight:140}
                );
                li.insertBefore(".uploadarea");
            }
        },
        addPreviewVideo: function(nextorder){
            //Agregamos un preview del video subido
            if(typeof nextorder === 'number'){
                var ul = this.$el.find('.row_gallery'),
                    li = null,
                    preview = null,
                    self = this;

                if(!ul){
                    ul = $('<ul/>').attr({"id": "row-gallery"}).addClass("connectedSortable").addClass("row_gallery").addClass("ui-sortable");
                }

                li = $("<li/>").attr({"data-id": "", "data-parent": this.parent_id, "data-key": "", "data-order": nextorder}).addClass("item-gallery").addClass("ui-sortable-handle");

                //Agregamos el preview de un video
                li.append($("<div/>").addClass("load_file_img"));
                li.append($("<div/>").addClass("load_file_img_bar"));
                li.append($("<img/>").attr({'src': '/static/gallstatic/img/video.png'}).css({'width': '200px', 'height': '140px', 'margin-top': '-176px'}));
                li.insertBefore(".uploadarea");
            }
        },
        submitVideo: function(){
            var self = this,
                video = $("#id_video_url").val(),
                data_send = {};

            $('.messages').removeClass('ok_request').removeClass('error_request');
            if(video !== ''){
                self.nextorder++;
                data_send = {
                        "order": self.nextorder,
                        "about":  $("#id_about_ifr").html(),
                        "tags": $("#id_tags").val(),
                        "administrator": $("#id_administrator option:selected").val(),
                        "high_definition": $("#id_high_definition").attr("checked") ? "on": "off",
                        "gallery": $("#id_gallery").val(),
                        "video": video
                };

                self.addPreviewVideo(self.nextorder);
                $.post('/gallery/admin/add/key/', data_send)
                    .done(function(data){
                        if(!data.error){
                            self.confirmItem(data.item, true);
                            $("#id_video_url").val('');
                            $('.messages').removeClass("error_request").addClass("ok_request").html('<p>Se ha realizado correctamente.</p>');
                        } else {
                            self.deletePreview(self.nextorder);
                            self.nextorder--;
                            $('.messages').removeClass("ok_request").addClass("error_request").html('<p>' + data.error + '</p>');
                        }
                    })
                    .fail(function(data){
                        self.deletePreview(self.nextorder);
                        self.nextorder--;
                        $('.messages').removeClass("ok_request").addClass("error_request").html('<p>Lo sentimos. Ha ocurrido un error al intentar agregar el video.</p>');
                });
            }
        },
        fileManager: function(){
            var self = this;
            var _u = _;

            $('.messages').removeClass('ok_request').removeClass('error_request');
            $("#fileupload").fileupload({
                dataType: "html",
                acceptFileTypes: /(\.|\/)(gif|jpe?g|png)$/i,
                maxFileSize: 10000000, // 5 MB
                imageMaxWidth: 200,
                imageMaxHeight: 140,
                submit: function(e, data){
                    self.nextorder++;
                    data.formData = {
                        "order": self.nextorder,
                        "about":  $("#id_about_ifr").html(),
                        "tags": $("#id_tags").val(),
                        "administrator": $("#id_administrator option:selected").val(),
                        "high_definition": $("#id_high_definition").attr("checked") ? "on": "off",
                        "gallery": $("#id_gallery").val()
                    };
                    self.currentUpload = self.nextorder;
                    self.addCanvaImage(data.files[0], self.nextorder);
                    //return false;
                },
                progress: function(e, data){
                    var progress = parseInt(data.loaded / data.total * 100, 10);
                    self.changeProgess(data.formData.order, progress);
                },
                done: function(e, data){
                    var result = null;
                    result = $.parseJSON(data.result);
                    if(!result.error){
                        $('.messages').removeClass("error_request").addClass("ok_request").html('<p>Se ha realizado correctamente.</p>');
                        self.currentOrder++;
                        self.confirmItem(result.item, false);
                    }else{
                        $('.messages').removeClass("ok_request").addClass("error_request").html('<p>' + result.error + '</p>');
                        self.deletePreview(data.formData.order);
                        self.nextorder--;
                    }
                },
                fail: function(e, data){
                    self.deletePreview(data.formData.order);
                    self.nextorder--;
                    $('.messages').removeClass("ok_request").addClass("error_request").html('<p>Lo sentimos. Ha ocurrido un error al intentar agregar la imagen.</p>');
                },
                change: function(e, data){
                    self.uploads = data.files.length;
                }
            });
        }
    });
});
