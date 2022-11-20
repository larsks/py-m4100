import pytest

from m4100.utils import parse_fixed_width_table

tests = (
    (
        (
            "one two three",
            "--- --- -----",
            "foo bar baz",
        ),
        [
            {"one": "foo", "two": "bar", "three": "baz"},
        ],
    ),
    (
        (
            "one two three",
            "--- --- -----",
            "foo     baz",
        ),
        [
            {"one": "foo", "two": "", "three": "baz"},
        ],
    ),
    (
        (
            "junk text",
            "",
            "nothing to see here",
            "",
            "one two three",
            "--- --- -----",
            "foo bar baz",
        ),
        [
            {"one": "foo", "two": "bar", "three": "baz"},
        ],
    ),
    (
        (
            "long                    ",
            "column long column      ",
            "one    two         three",
            "------ ----------- -----",
            "foo    bar         baz",
        ),
        [
            {"long column one": "foo", "long column two": "bar", "three": "baz"},
        ],
    ),
)


@pytest.mark.parametrize("given,expected", tests)
def test_parse_fixed_width_table(given, expected):
    res = parse_fixed_width_table(given)
    assert res == expected
