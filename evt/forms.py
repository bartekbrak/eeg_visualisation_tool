# coding=utf-8
from __future__ import unicode_literals
from wtforms import Form, FileField, IntegerField, FloatField, StringField


class ServerForm(Form):
    data_file = FileField(
        'Dane',
        description='Plik Excel 2007/2010/2013.')
    clip = FileField(
        'Klip',
        description='Klip z nagraniem. MP4 jest rekomendowanym formatem'
    )
    no_of_plots = StringField(
        'Liczba wykresów',
        default="1, 1",
        description='Liczba wykresów na arkusz. Cyfry rozdzielone przecinkami.'
    )
    sampling_rate = IntegerField(
        'Próbkowanie',
        default=333,
        description='Częstotliwość próbkowania zaebranych danych'
    )
    y_margin = FloatField(
        'Margines Y',
        default=0.2,
        description='Odległość od górnej i dolnej krawędzi wykresu przy '
                    'największym wykresie'
    )
    client_name = StringField(
        'Nazwa klienta',
        default='Nazwa klienta',
    )
    research_name = StringField(
        'Nazwa Badania',
        default='Nazwa Badania',
    )
    date = StringField(
        'Data badania',
        default='2015-08-08',
    )
    sample_size = StringField('Wielkośc próby', default='1000')
    plot_title = StringField(
        'Nazwa zakładki',
        default='EEG Dom Badawczy Maison',
        description='Nazwa zakładki w przeglądarce. pliku wynikowego.'
    )
