import itertools
from operator import itemgetter
import random
from numpy import mean
from evt.constants import data_column_name

def to_tuple(what):
    if isinstance(what, basestring):
        return what,
    else:
        return what

def average_yaxis_by_properties(column_names, rows):
    """
    This will produce tree-like values combining all column_names.
    rows will be grouped by first column_name, then every result by next,
    and so on.
    The result has depth of len(column_names).
    Not used directly in the application but left for extensibility.
    """
    # TODO: find out if numpy can do this
    sort_key = itemgetter(*column_names)
    sorted_by_column_name = sorted(rows, key=sort_key)
    grouper = itertools.groupby(
        sorted_by_column_name, sort_key
    )
    for column_values, grouped_data_rows in grouper:
        description = dict(zip(column_names, to_tuple(column_values)))
        grouped = mean(
            [data_row[data_column_name] for data_row in grouped_data_rows],
            axis=0
        )
        yield description, grouped, column_names


def average_yaxis_by_properties_separate(column_names, rows):
    """
    This will produce a group for each column_name without combining them.
    The result has depth of 1.
    Note that we want to pass the tuple.
    """
    for column_name in column_names:
        for _ in average_yaxis_by_properties((column_name, ), rows):
            yield _


def get_random_colour():
    r = lambda: random.randint(0, 196)
    return '#%02X%02X%02X' % (r(), r(), r())
