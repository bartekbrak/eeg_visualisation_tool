import csv
from openpyxl import load_workbook


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
            unicode_row.update({unicode(key, 'utf-8'): value})
        yield unicode_row


def get_from_excel(filename, column_name_map):
    wb = load_workbook(filename)
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
            restkey='as'
        )
        return list(reader)
