"use strict";

function init_maps() {
    document.querySelectorAll('.wagtail-geo-widget-map').forEach(function(el) {
        var point = {lat: parseFloat(el.getAttribute('data-lat')), lng: parseFloat(el.getAttribute('data-lng'))},
            map = new google.maps.Map(el, {
                zoom: parseInt(el.getAttribute('data-zoom')),
                center: point
            }),
            marker = new google.maps.Marker({
                position: point,
                map: map
            });
    });
}
