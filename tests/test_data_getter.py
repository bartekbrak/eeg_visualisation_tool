from src.data_getter import get_from_csv, get_from_excel

column_names = ('peron_name', 'sex', 'age', 'favourite_brand')

def test_getting_from_csv():
    result = get_from_csv('tests/test_data/tomek.csv', column_names)
    assert isinstance(result, list)
    assert len(result) ==  15
    for row in result:
        assert isinstance(row, dict)
        assert sorted(('as',) + column_names) == sorted(row.keys())
        assert all(isinstance(as_value, float) for as_value in row['as'])


def test_getting_from_excel():
    result = get_from_excel('tests/test_data/dane_tymbark.xlsx', column_names)
    assert isinstance(result, list)
    assert len(result) == 15
    for row in result:
        assert isinstance(row, dict)
        assert sorted(('as',) + column_names) == sorted(row.keys())
        assert all(isinstance(as_value, float) for as_value in row['as'])
