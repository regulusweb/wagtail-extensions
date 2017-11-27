"use strict";

function init_maps() {
    var maps = $('.wagtail-geo-widget-map');

    maps.each(function(idx) {
        var $map_el = $(this),
            point = {lat: $map_el.data('lat'), lng: $map_el.data('lng')},
            map = new google.maps.Map($map_el[0], {
                zoom: $map_el.data('zoom'),
                center: point
            }),
            marker = new google.maps.Marker({
                position: point,
                map: map
            });
    });
}
