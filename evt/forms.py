from wtforms import Form, StringField, FileField, IntegerField, FloatField


class ServerForm(Form):
    file = FileField(
        description='Excel data source file. CSV will be supported soon.')
    movie = FileField(
        description='Ad movie file. Any format supported by modern browsers '
                    'is fine: mp4/ogm etc.'
    )
    no_of_plots = IntegerField(
        default=2,
        description='How many plots to display?'
    )
    sampling_rate = IntegerField(
        default=333,
        description='EEG sampling rate the data was collected with.'
    )
    y_margin = FloatField(
        default=0.2,
        description='The amount of empty space above and below the lines. Padding.'
    )
