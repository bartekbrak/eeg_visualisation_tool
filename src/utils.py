from itertools import imap
import itertools
import random
from bokeh.models import Range1d
from bokeh.plotting import figure


def arithmetic_mean(*list_):
    return float(sum(list_)) / len(list_) if len(list_) > 0 else float('nan')


def keys(*args):
    def wrapper(d):
        values = [d[arg] for arg in args]
        return values
    return wrapper


def group_by(by, data):
    column_sorted = sorted(data, key=keys(*by))
    result = {}
    for key, group in itertools.groupby(column_sorted, keys(*by)):
        description = dict(zip(by, key))
        description_str = '__'.join(
            ['{}_{}'.format(k, v) for k, v in description.items()]
        )
        grouped = list(
            imap(
                arithmetic_mean,
                *[person['as'] for person in list(group)]
            )
        )
        result[description_str] = {
            'description': description,
            'grouped': grouped
        }
    return result


def get_random_colour():
    r = lambda: random.randint(0, 255)
    return '#%02X%02X%02X' % (r(), r(), r())


def get_figure(
    x_ms,
    width=800,
    title='eeg visualisation grouped',
    x_axis_label='time',
    y_axis_label='y', tools='save', **kwargs
):
    return figure(
        title=title,
        x_axis_label=x_axis_label,
        y_axis_label=y_axis_label,
        tools=tools,
        width=width,
        x_range=Range1d(0, x_ms),
        x_axis_type='datetime',
        **kwargs
    )
