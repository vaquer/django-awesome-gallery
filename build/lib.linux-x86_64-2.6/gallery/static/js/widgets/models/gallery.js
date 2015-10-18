define(['underscore', 'backbone'], function (_, BB) {
    return BB.Model.extend({
        url: null,
        defaults: {
            id: null,
            slug: null,
            name: null,
            about: null,
            high_definition: false,
            enabled: false,
            count: 0,
            permalink: null,
            tags: [],
            first_foto: null,
            thumbnails_gallery: null,
            related_galeries: null
        }
    });
});