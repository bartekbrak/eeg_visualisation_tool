import re

import pytest

from evt.constants import column_name_map
from evt.data_getter import get_from_excel
from evt.utils import group_by, arithmetic_mean, get_random_colour


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


@pytest.mark.parametrize('grouping_by,expected', test_data)
def test_group_by(grouping_by, expected):
    data = get_from_excel('tests/test_data/dane_tymbark.xlsx', column_name_map)
    result = group_by(grouping_by, data)
    for one_result, one_expected in zip(result, expected):
        description, grouped = one_result
        expected_description, expected_rounded_mean = one_expected
        assert description == expected_description
        assert round(sum(grouped), 2) == expected_rounded_mean


def test_arithmetic_mean():
    # actual data from dane_tymbark.xlsx for first frame of age=1 group
    data = (
        1.26769868117818, 0.813653674494978, 1.46063006576379,
        1.19390966628079, 0.17139155694351, -0.0572934016590679,
        0.107614463265602
    )
    assert arithmetic_mean(*data) == 0.7082292437525403


def test_arithmetic_mean_on_empty():
    # Some might say that ZeroDivisionError is wrong here. True, but what would
    # raising, let's say, a RuntimeError with a string description add here?
    # Keeping the function short makes it easier to debug, you'll spot the
    # problem right on. Don't be too paranoid ;). There bigger problems
    # elsewhere
    with pytest.raises(ZeroDivisionError):
        arithmetic_mean()


def test_get_random_colour():
    assert re.match('#[A-F0-9]{6}', get_random_colour())
