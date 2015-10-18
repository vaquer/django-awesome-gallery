define(['jquery', 'underscore', 'backbone', 'gallery/widgets/collections/set_items', 'GallSettings', 'bootstrap'], 
    function ($, _, BB, ItemsCollectionRequire) {
    return BB.View.extend({
        el: $('#box_edit_form'),
        plural: false,
        collectionObj: null,
        events: {
            'click .img_item_multiple': 'eventFillForm',
            'click .close': 'hideBox',
        },
        initialize: function(options){
            console.log(ItemsCollectionRequire);
            this.collectionObj = new ItemsCollectionRequire();
        },
        render: function(){
            this.showBox(true);
        },
        addItemToCollection: function(object){
            this.collectionObj.add(object);
        },
        refreshBox: function(objects) {
            this.$el.find('.modal-body .forms').html(objects.form);
            this.fillPreviewsAndForm();
            this.manageLoading(loading);
        },
        fillPreviewsAndForm: function(){
            var html = '<ul class="widget-editor-list-img">';
            this.plural = (this.collectionObj.length > 1 ? true : false);
            _.each(this.collectionObj.models, function(model){
                html += '<li class="row-gallery-editor" data-order="' + model.get('order') + '" data-key="' + model.get('key_name') + '">' + model.get('html') + '</li>';
            });
            html += '</ul>';
            this.$el.find('.modal-body .preview').html(html);
            this.fillForm((this.plural ? 1 : null));
        },
        fillForm: function(order){
            var item = null;

            if(!order){
                item = this.collectionObj.firs();
            }

            item = !order ? this.collectionObj.firs() : this.collectionObj.where({"order": order});

            $("#id_name").val(item.get('name'));
            $("#id_about").val(item.get('about'));
            $("#id_path").val(item.get('path'));
            $("#id_order").val(item.get('order'));
            $("#id_administrator").val(item.get('administrator'));
            $.each(item.tags.split(','), function(i, e){
                $("#id_tags option[value='" + e + "']").prop("selected", true);
            });
            $("#id_high_definition").prop((item.get('hd') ? 'checked' : ''))
            $("#id_enabled").prop((item.get('enabled') ? 'checked' : ''))
        },
        eventFillForm: function(e){
            if(plural){
                this.fillForm($(e.currentTarget).attr('data-order'));
            }
        },
        manageLoading: function(loading){
            this.$el.find('.modal-body .preview').css({'display': (loading ? 'none' : 'block')});
            this.$el.find('.modal-body .forms').css({'display': (loading ? 'none' : 'block')});
            this.$el.find('.modal-body .loading').css({'display': (loading ? 'block' : 'none')});
        },
        showBox: function(loading){
            if(this.$el.attr('aria-hidden') === 'true')
            {
                this.manageLoading(loading);
                this.$el.modal('show');
            }
        },
        hideBox: function(){
            if(this.$el.attr('aria-hidden') === 'false')
            {
                this.$el.modal('hide');
            }
        }
    });
});