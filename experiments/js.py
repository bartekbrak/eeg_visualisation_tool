hover_js = "hover_position=cb_data['geometry']['x'] / 1000;"
tap_js = '''
    if (cb_obj.get('name') == '%s') {
    if (hover_active) {
        // video.currentTime = hover_position;
        video.play();
        hover_active = false;
    } else {
        video.pause();
        hover_active = true;
    }
    }
'''