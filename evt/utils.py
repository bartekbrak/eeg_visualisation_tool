from itertools import imap
import itertools
from operator import itemgetter
import random
from evt.constants import data_column_name


def arithmetic_mean(*list_):
    return float(sum(list_)) / len(list_) if len(list_) > 0 else float('nan')


def group_by(column_names, rows):
    sorted_by_column_name = sorted(rows, key=itemgetter(*column_names))
    grouper = itertools.groupby(
        sorted_by_column_name, itemgetter(*column_names)
    )
    for column_values, grouped_data_rows in grouper:
        description = _get_description(column_names, column_values)
        grouped = imap(
            arithmetic_mean,
            *[data_row[data_column_name] for data_row in grouped_data_rows]
        )
        yield description, grouped


def _get_description(column_names, column_values):
    if len(column_names) == 1:
        column_values = (column_values,)
    return dict(zip(column_names, column_values))


def get_random_colour():
    r = lambda: random.randint(0, 255)
    return '#%02X%02X%02X' % (r(), r(), r())
