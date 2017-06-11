""" Input-output operations and wrappers for the parser """

from ltcstm.storage import MasterData


def parse_string(string, bib=""):
    """ Parses a string and returns the associated MasterData object """

    return MasterData(string, bib)


def parse_file(filename, bib=""):
    """ Parses the file 'filename' and returns the associated MasterData object """
    with open(filename, "r") as file:
        input_data = file.read()

    return parse_string(input_data, bib)
