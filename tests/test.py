""" Integration test using some of Daniel's notes """

from ltcstm.io import parse_to_files

def test_integration():
    """ Integration test """
    parse_to_files("tests/integration_test/test.tex",
                   "tests/integration_test/bib.bib",
                   "tests/integration_test/s.yaml",
                   "tests/integration_test/l.yaml",
                   "tests/integration_test/kp.yaml")

    return

if __name__ == "__main__":
    test_integration()