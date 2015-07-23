from IPython import embed
from IPython.html import widgets  # Widget definitions.
# from traitlets import Unicode # Traitlet needed to add synced attributes to the widget.
from IPython.utils.traitlets import Unicode, Bytes, CBytes, TraitType
from io import BytesIO


class MyUnicode(TraitType):
    """A trait for unicode strings."""

    default_value = ''
    info_text = 'a unicode string'

    def validate(self, obj, value):
        # print type(value)
        # print dir(obj)
        return value
    #     if isinstance(value, bytes):
    #         try:
    #             return value.decode('ascii', 'strict')
    #         except UnicodeDecodeError:
    #             pass
    #             # msg = "Could not decode {!r} for unicode trait '{}' of {} instance."
    #             # raise TraitError(msg.format(value, self.name, class_of(obj)))
    #     self.error(obj, value)

class FileWidget(widgets.DOMWidget):
    _view_name = Unicode('FilePickerView', sync=True)
    value = MyUnicode(sync=True)
    filename = Unicode(sync=True)

    def __init__(self, **kwargs):
        """Constructor"""
        widgets.DOMWidget.__init__(self, **kwargs)  # Call the base.

        # Allow the user to register error callbacks with the following signatures:
        #    callback()
        #    callback(sender)
        self.errors = widgets.CallbackDispatcher(accepted_nargs=[0, 1])

        # Listen for custom msgs
        self.on_msg(self._handle_custom_msg)

    def _handle_custom_msg(self, content):
        """Handle a msg from the front-end.

        Parameters
        ----------
        content: dict
            Content of the msg."""
        if 'event' in content and content['event'] == 'error':
            self.errors()
            self.errors(self)



# file_widget
def get_file_widget(stringio):
    file_widget = FileWidget()

    # Register an event to echo the filename when it has been changed.
    def file_loading():
        print("Loading %s" % file_widget.filename)

    file_widget.on_trait_change(file_loading, 'filename')

    # Register an event to echo the filename and contents when a file
    # has been uploaded.
    def file_loaded(name, new):
        # stringio.write(file_widget.value.encode('utf-8'))
        stringio['csv'] = BytesIO(file_widget.value.encode('utf-8'))
        # stringio.write(file_widget.value)
        # with open('suck.xlsx', 'w') as f:
        #     f.write(file_widget.value)
        print("Loaded, file contents: %s" % 'file_widget.value')

    file_widget.on_trait_change(file_loaded, 'value')

    # Register an event to print an error message when a file could not
    # be opened.  Since the error messages are not handled through
    # traitlets but instead handled through custom msgs, the registration
    # of the handler is different than the two examples above.  Instead
    # the API provided by the CallbackDispatcher must be used.
    def file_failed(*args, **kwargs):
        print("Could not load file contents of %s" % file_widget.filename)

    file_widget.errors.register_callback(file_failed)
    return file_widget