from wtforms import Form, FileField, IntegerField, FloatField, StringField


class ServerForm(Form):
    data_file = FileField(
        description='Excel data source file. CSV will be supported soon.')
    clip = FileField(
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
        description='The amount of empty space above and below the lines. '
                    'Padding.'
    )
    client_name = StringField(
        default='Nazwa klienta',
        description='Client\'s name'
    )
    research_name = StringField(
        default='Nazwa Badania',
        description='Research title'
    )
    date = StringField(
        default='2015-08-08',
        description=''
    )
    sample_size = StringField(
        default='1000',
        description='Sample size'
    )
    plot_title = StringField(
        default='EEG Visualisation Tool',
        description='The name of the file, displayed in browser tab and '
                    'window name.'
    )
