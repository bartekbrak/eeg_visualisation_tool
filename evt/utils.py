import itertools
import os
import pickle
from operator import itemgetter

from numpy import mean

from evt.constants import color_pickle, numerical_data_column_name


def to_tuple(what):
    if isinstance(what, (basestring, int, float)):
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
            [data_row[numerical_data_column_name] for data_row in
             grouped_data_rows],
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
        for _ in average_yaxis_by_properties((column_name,), rows):
            yield _


distinct_colors = [
    '#FF0000', '#A66C29', '#39E639', '#266399', '#554359', '#F20000',
    '#403830', '#00F2C2', '#162859', '#D26CD9', '#330000', '#FFBF40',
    '#006652', '#00008C', '#66005F', '#994D4D', '#998A4D', '#56736D',
    '#000073', '#330D2B', '#7F2200', '#CCFF00', '#00CCFF', '#000066',
    '#F20081', '#401D10', '#2B330D', '#005266', '#6060BF', '#8C466C',
    '#D9896C', '#BFE673'
]
cycler = itertools.cycle(distinct_colors)


def get_random_colour():
    return cycler.next()


def get_pickled_colors(filename=color_pickle):
    if not os.path.isfile(filename):
        print 'no pickles'
        return distinct_colors[:20]
    with open(filename) as f:
        return pickle.load(f)
