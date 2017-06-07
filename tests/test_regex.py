""" Tests for ltcstm.regex.py """

from ltcstm.regex import text_replace
from ltcstm.regex import find_items

def test_text_replace():
    """ Tests for the text_replace function - recursive """

    test_data = [
        ["hello world dogs", ["hello", "world", "dogs"], ["x", "y", "z"]],
    ]

    expected_outcomes = [
        "x y z",
    ]

    for test, expected, i in zip(test_data, expected_outcomes, range(len(test_data))):
        assert text_replace(test[0], test[1], test[2]) == expected, "failed on test 1.{}".format(i)


def test_find_items():
    """ Tests for the quick wrapper over regex """

    test_data = [
        ["hello dogs world", "hello"],
    ]

    expected_outcomes = [
        ["hello"],
    ]

    for test, expected, i in zip(test_data, expected_outcomes, range(len(test_data))):
        assert find_items(test[0], test[1]) == expected, "failed on test 1.{}".format(i)
