import re

import pytest

from evt.data_getter import get_from_excel
from evt.utils import average_yaxis_by_properties, get_random_colour

# rather than checking that the content of a group has
# same content, let's compare against some calculation for brevity, a sum,
# there is low risk of uncaught errors if some silly flat data was used
test_data = (
    (
        ('age',),
        (
            ({'age': 1}, 15.35),
            ({'age': 2}, 11.08)
        )
    ),
    (
        ('age', 'sex'),
        (
            ({'age': 1, 'sex': 1}, 5.45),
            ({'age': 1, 'sex': 2}, 22.78),
            ({'age': 2, 'sex': 1}, 16.32),
            ({'age': 2, 'sex': 2}, 2.35),
        )
    ),
)


# @pytest.mark.parametrize('grouping_by,expected', test_data)
# def test_average_yaxis_by_properties(grouping_by, expected):
#     data = get_from_excel('tests/test_data/dane_tymbark.xlsx', column_name_map)
#     result = average_yaxis_by_properties(grouping_by, data)
#     for one_result, one_expected in zip(result, expected):
#         description, grouped = one_result
#         expected_description, expected_rounded_mean = one_expected
#         assert description == expected_description
#         assert round(sum(grouped), 2) == expected_rounded_mean


def test_get_random_colour():
    assert re.match('#[A-F0-9]{6}', get_random_colour())
