""" Input-output operations and wrappers for the parser """

from ltcstm.storage import MasterData, split_data


def parse_string(string, bib=""):
    """ Parses a string and returns the associated MasterData object """

    return MasterData(string, bib)


def parse_file(filename, bib=""):
    """ Parses the file 'filename' and returns the associated MasterData object """
    with open(filename, "r") as file:
        input_data = file.read()

    return parse_string(input_data, bib)


def grab_data(string, bib=""):
    """ Grabs two dictionaries and a list:
        + secs - the sections (with structure section[name][data] = the markdown, and assc. kps)
        + lecs - the lectures (same as above)
        + kps - the keypoints """

    return split_data(MasterData(string, bib))
