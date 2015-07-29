from itertools import imap
import itertools
from operator import itemgetter
import random


def arithmetic_mean(*list_):
    return float(sum(list_)) / len(list_) if len(list_) > 0 else float('nan')


def group_by(by, data):
    sorted_by_column = sorted(data, key=itemgetter(*by))
    result = {}
    for key, group in itertools.groupby(sorted_by_column, itemgetter(*by)):
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
            'y_series': grouped,
            'color': get_random_colour()
        }
    return result


def get_random_colour():
    r = lambda: random.randint(0, 255)
    return '#%02X%02X%02X' % (r(), r(), r())
