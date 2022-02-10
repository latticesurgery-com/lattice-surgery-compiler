import pytest

from lsqecc.utils import is_power_of_two


@pytest.mark.parametrize(
    "n, expected_value",
    [
        (0, False),
        (1, True),
        (2, True),
        (3, False),
        (4, True),
        (6, False),
        (1024, True),
        (2**63, True),
        (2**64, True),
        (2**65, True),
        (2**65+1, False),
        (-1, False),
        (-2, False),
    ],
)
def test_is_power_of_two(n: int, expected_value: bool):
    assert is_power_of_two(n) == expected_value
