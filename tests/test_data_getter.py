from evt.constants import column_name_map
from evt.data_getter import get_from_csv, get_from_excel


def test_getting_from_csv():
    result = get_from_csv('tests/test_data/tomek.csv', column_name_map)
    assert isinstance(result, list)
    assert len(result) == 15
    for row in result:
        assert isinstance(row, dict)
        assert sorted(('as',) + column_name_map) == sorted(row.keys())
        assert all(isinstance(as_value, float) for as_value in row['as'])


def test_getting_from_excel():
    result = get_from_excel(
        'tests/test_data/dane_tymbark.xlsx', column_name_map)
    assert isinstance(result, list)
    assert len(result) == 15
    for row in result:
        assert isinstance(row, dict)
        assert sorted(('as',) + column_name_map) == sorted(row.keys())
        assert all(isinstance(as_value, float) for as_value in row['as'])
