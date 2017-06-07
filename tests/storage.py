""" Tests for storage.py """

from ltcstm.storage import Keypoint

def test_keypoint_extract_keypoint():
    """ Test for Keypoint.extract_keypoint() """
    test_data = [
        r"%%\keypoint{This is a call}",
        r"\keypoint{This is a call two}",
        r"\keypt{This is not a call}",
        r"HELLO WORLD",
        r"%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\keypoint{$$ \int \cos(x) \mathrm{d}x $$}"
    ]

    expected_outcomes = [
        r"This is a call",
        r"This is a call two",
        r"",
        r"",
        r"$$ \int \cos(x) \mathrm{d}x $$"
    ]

    for test, expected in zip(test_data, expected_outcomes):
        keypt = Keypoint(test, 0, 0)
        assert keypt.output_data == expected

    return

