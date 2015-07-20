require(["widgets/js/widget", "widgets/js/manager"], function(widget, manager){

    var FilePickerView = widget.DOMWidgetView.extend({
        render: function(){
            // Render the view.
            this.setElement($('<input />')
                .attr('type', 'file'));
        },
        
        events: {
            // List of events and their handlers.
            'change': 'handle_file_change',
        },
       
        handle_file_change: function(evt) { 
            // Handle when the user has changed the file.
            
            // Retrieve the first (and only!) File from the FileList object
            var file = evt.target.files[0];
            if (file) {

                // Read the file's textual content and set value to those contents.
                var that = this;
                var file_reader = new FileReader();
                file_reader.onload = function(e) {
                    that.model.set('value', e.target.result);
                    that.touch();
                }
                file_reader.readAsText(file);
            } else {

                // The file couldn't be opened.  Send an error msg to the
                // back-end.
                this.send({ 'event': 'error' });
            }

            // Set the filename of the file.
            this.model.set('filename', file.name);
            this.touch();
        },
    });
        
    // Register the DatePickerView with the widget manager.
    manager.WidgetManager.register_widget_view('FilePickerView', FilePickerView);
});
