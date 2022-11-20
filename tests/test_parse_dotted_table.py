import pytest

from m4100.utils import parse_dotted_table

tests = (
    (
        (
            "one.... foo",
            "two.... bar",
            "three... baz",
        ),
        {"one": "foo", "two": "bar", "three": "baz"},
    ),
    (
        (
            "one.... foo",
            "two....",
            "three... baz",
        ),
        {"one": "foo", "two": None, "three": "baz"},
    ),
)


@pytest.mark.parametrize("given,expected", tests)
def test_dotted_table(given, expected):
    res = parse_dotted_table(given)
    assert res == expected
