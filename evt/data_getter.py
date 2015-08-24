from __future__ import unicode_literals
from collections import defaultdict
from bokeh.models import ColumnDataSource
import numpy
from openpyxl import load_workbook
from evt import memory
from evt.constants import data_column_name
from evt.models import Line
from evt.utils import get_random_colour


# @memory.cache
def get_from_excel(filename):
    print 'running get_from_excel', filename
    wb = load_workbook(filename, read_only=True, data_only=True)
    sheets = [sheet for sheet in wb.worksheets if bool(sheet.columns[0])]
    ret = []
    for sheet in sheets:
        rows = list(sheet.rows)
        filter_column_names = get_filter_column_names(rows.pop(0))
        data = [row_as_dict(row, filter_column_names) for row in rows]
        ret.append({
            'filter_column_names': filter_column_names,
            'data': data,
            'title': sheet.title
        })
    return ret


def get_filter_column_names(first_row):
    return [
        cell.value for cell in first_row
        if cell.value and not cell.value.startswith(data_column_name)
    ]


def row_as_dict(row, filter_column_names):
    values = [column.value for column in row if column.value is not None]
    result = {}
    for name in filter_column_names:
        result[name] = values.pop(0)
    result[data_column_name] = values
    return result


def get_video_data(filename):
    with open(filename) as f:
        return f.read().encode('base64')


def get_mean(data, axis=None):
    return numpy.mean([row[data_column_name] for row in data], axis)


def grouper(data, grouped_by, sampling_rate, grouper_f):
    line_groups = defaultdict(list)
    for description, y_series, filter_names in grouper_f(grouped_by, data):
        x_range = range(0, len(y_series) * sampling_rate, sampling_rate)
        source = ColumnDataSource(data=dict(x=x_range, y=y_series))
        key = ', '.join(filter_names)
        line_groups[key].append(
            Line(y_series, source, description, get_random_colour())
        )
    return line_groups


def continuous_array(x, y):
    # FIXME: I bet numpy can do this on its own
    assert sorted(x) == x, 'Expecting sorted x'
    assert len(x) == len(y), 'fuck'
    ret = []
    for i, (first_x, first_y) in enumerate(zip(x, y)):
        if i == len(x) - 1:
            break
        second_x = x[i + 1]
        second_y = y[i + 1]
        xgap = second_x - first_x
        space = numpy.linspace(first_y, second_y, num=xgap, endpoint=False)
        ret += list(space)
    return ret
