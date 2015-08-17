from __future__ import unicode_literals
from openpyxl import load_workbook
from evt.constants import data_column_name


def get_from_excel(filename):
    wb = load_workbook(filename, read_only=True, data_only=True)
    sheets = [sheet for sheet in wb.worksheets if bool(sheet.columns[0])]
    ret = []
    for sheet in sheets:
        rows = list(sheet.rows)
        filter_column_names = get_filter_column_names(rows.pop(0))
        data = [row_as_dict(row, filter_column_names) for row in rows]
        ret.append({
            'filter_column_names': filter_column_names,
            'data': data
        })
    return ret


def get_filter_column_names(first_row):
    return [
        cell.value for cell in first_row
        if not cell.value.startswith(data_column_name)
    ]


def row_as_dict(row, filter_column_names):
    values = [column.value for column in row]
    result = {}
    for name in filter_column_names:
        result[name] = values.pop(0)
    result[data_column_name] = values
    return result
