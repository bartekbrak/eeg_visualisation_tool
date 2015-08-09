from __future__ import unicode_literals
import csv
from openpyxl import load_workbook
from evt.constants import data_column_name


def unicode_dict_reader(utf8_data, restkey, skip_header=True, **kwargs):
    csv_reader = csv.DictReader(utf8_data, restkey=restkey, **kwargs)
    if skip_header:
        csv_reader.next()
    for row in csv_reader:
        unicode_row = {}

        for key, value in row.iteritems():
            if key == restkey:
                value = map(float, value)
            else:
                value = unicode(value, 'utf-8')
            unicode_row.update({key: value})
        yield unicode_row


def get_from_excel(filename, column_name_map):
    wb = load_workbook(filename, read_only=True, data_only=True)
    sheet = wb.get_active_sheet()
    result = [
        asdict(person, column_name_map)
        for person in
        sheet.rows
        ]
    return result[1:]


def asdict(person, column_name_map):
    values = [column.value for column in person]
    result = {}
    for name in column_name_map:
        result[name] = values.pop(0)
    result['as'] = values
    return result


def get_from_csv(filename, column_names):
    with open(filename) as f:
        reader = unicode_dict_reader(
            utf8_data=f,
            fieldnames=column_names,
            restkey=data_column_name
        )
        return list(reader)


def get_from_f(f, column_names):
    reader = unicode_dict_reader(
        utf8_data=f,
        fieldnames=column_names,
        restkey=data_column_name
    )
    return list(reader)
