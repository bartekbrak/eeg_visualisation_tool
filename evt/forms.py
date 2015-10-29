# coding=utf-8
from __future__ import unicode_literals

"""
no_of_plots is misleading, this holds gauge colours
"""

from wtforms import (
    FieldList,
    FileField,
    FloatField,
    Form,
    IntegerField,
    StringField,
    TextAreaField,
    FormField)

class GaugeColors(Form):
    colors = FieldList(
        unbound_field=StringField(),
    )

class ServerForm(Form):
    data_file = FileField(
        'Dane',
        description='Plik Excel 2007/2010/2013.')
    clip = FileField(
        'Klip',
        description='Klip z nagraniem. MP4 jest rekomendowanym formatem'
    )
    no_of_plots = FieldList(
        label='Liczba<br>wykresów',
        unbound_field=FormField(GaugeColors),
        description='Każdy rząd reprezentuje jeden arkusz z danych zawierający '
                    'jeden bądź więcej wykresów. Każda para kolorów '
                    'reprezentuje jeden wykres opisany dwoma kolorami: poniżej '
                    'i powyżej średniej.'
    )
    sampling_rate = IntegerField(
        'Próbkowanie',
        default=100,
        description='Częstotliwość próbkowania zaebranych danych'
    )
    y_margin = FloatField(
        'Margines Y',
        default=0.2,
        description='Odległość od górnej i dolnej krawędzi wykresu przy '
                    'największym wykresie'
    )
    plot_title = StringField(
        'Nazwa zakładki',
        default='EEG Dom Badawczy Maison',
        description='Nazwa zakładki w przeglądarce. pliku wynikowego.'
    )
    colors = FieldList(
        label='Paleta',
        unbound_field=StringField(),
    )
    client_info_markdown = TextAreaField(
        'Ramka z danymi o badaniu',
        default='**Nazwa Klienta**: Nazwa Klienta\n'
                '**Nazwa Badania**: Nazwa Badania\n'
                '**Data**: 2015-08-08\n'
                '**Próba**: 100',
        description='Składnia <a href="https://en.wikipedia.org/wiki/'
                    'Markdown#Example" target=_blank>Markdown</a> albo HTML.'
    )
