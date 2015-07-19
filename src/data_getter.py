import csv


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


def get_from_excel(filename, column_names):
    pass


def get_from_csv(filename, column_names):
    with open(filename) as f:
        reader = unicode_dict_reader(
            utf8_data=f,
            fieldnames=column_names,
            restkey='as'
        )
        return list(reader)
