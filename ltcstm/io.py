""" Input-output operations and wrappers for the parser """

from ltcstm.storage import MasterData, split_data
import json


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

    return split_data(parse_string(string, bib))


def process_file(filename, bib=""):
    """ Grabs two dictionaries and a list:
        + secs - the sections (with structure section[name][data] = the markdown, and assc. kps)
        + lecs - the lectures (same as above)
        + kps - the keypoints """

    return split_data(parse_file(filename, bib))


def parse_to_files(filename, bib="",
                   fn_sections="sections.json",
                   fn_lectures="lectures.json",
                   fn_kps="kps.json"):
    """ Opens the file, filename, and does a processing run and saves them as json files. """

    secs, lecs, kps = process_file(filename, bib)

    with open(fn_sections, "w") as file:
        json.dump(secs, file)

    with open(fn_lectures, "w") as file:
        json.dump(lecs, file)

    with open(fn_kps, "w") as file:
        json.dump(kps, file)

    return
