from evt.constants import column_name_map
from evt.data_getter import get_from_excel
from evt.utils import group_by


def test_group_by():
    data = get_from_excel('tests/test_data/dane_tymbark.xlsx', column_name_map)
    grouping_by = column_name_map[1:]
    result = group_by(grouping_by, data)
    assert isinstance(result, dict)
    assert len(result) == 8
    # rather than checking that the content of averaged group has
    # same contents, let's calculate a sum to compare, just shorter
    expected = {
        'age_2__favourite_brand_2__sex_1': -8.216711117092892,
        'age_2__favourite_brand_2__sex_2': -12.355994693496312,
        'age_1__favourite_brand_1__sex_2': 32.98390846459878,
        'age_1__favourite_brand_1__sex_1': 34.96046387907767,
        'age_1__favourite_brand_2__sex_2': 12.575378836605239,
        'age_1__favourite_brand_2__sex_1': -9.30574034274511,
        'age_2__favourite_brand_1__sex_1': 32.66971883880301,
        'age_2__favourite_brand_1__sex_2': 31.754965032960115,

    }
    for k, v in result.items():
        for column_name in grouping_by:
            assert column_name in k
        assert 'description' in v
        assert 'y_series' in v
        assert 'color' in v
        assert expected[k] == sum(v['y_series'])
