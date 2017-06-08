""" Tests for storage.py """

from ltcstm.storage import Keypoint, PreprocessedData, PostprocessedData

def test_keypoint_extract_keypoint():
    """ Test for Keypoint.extract_keypoint() """

    # First test the extraction of data

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

    for test, expected, i in zip(test_data, expected_outcomes, range(len(test_data))):
        keypt = Keypoint(test, 0, 0)
        assert keypt.output_data == expected, "failed on test 1.{}".format(i)

    # Now we'll test the expected outcomes from the pandoc conversion

    test_data = [
        r"%%\keypoint{This is a \emph{call}}",
    ]

    expected_outcomes = [
        "This is a *call*\n",
    ]

    for test, expected, j in zip(test_data, expected_outcomes, range(len(test_data))):
        keypt = Keypoint(test, 0, 0, run_pandoc=True)
        assert keypt.output_data == expected, "failed on test 2.{}".format(j)

    return


def test_find_start_stop():
    """ Tests the MasterData.find_start_stop function """

    test_data = [
        ["""<x>
        blah
        s
        <y>
        ssd""", ["<x>", "<y>"]],
    ]

    expected_outcomes = [
        [(0, 3), (3, 4)],
    ]

    for test, expected, j in zip(test_data, expected_outcomes, range(len(test_data))):
        master = PostprocessedData(PreprocessedData(test[0]))
        assert master.find_start_stop(test[0], test[1]) == expected, "failed on test 2.{}".format(j)

    return
