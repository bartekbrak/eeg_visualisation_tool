hover_js = "hover_position=cb_data['geometry']['x'] / 1000;"
tap_js = '''
    if (cb_obj.get('name') == '%s') {
    if (ready_to_play) {
        video.play();
        ready_to_play = false;
    } else {
        video.pause();
        ready_to_play = true;
    }
    }
'''