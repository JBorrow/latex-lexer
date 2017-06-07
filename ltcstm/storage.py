""" Contains the objects and data structures used in the processing of LaTeX
    documents, including the keypoints storage structure.

    Date Created: 2017-06-07
    Created By: Josh Borrow """


import re
import pypandoc

import ltcstm.regex


class Keypoint(object):
    """ Basic keypoint storage and extraction class.

        If run_pandoc is taken to be True, pandoc is ran on the internal text.

        Position should be given as the line number that the keypoint as found at. """

    def __init__(self, raw_data, uid, position, run_pandoc=False):
        self.raw_data = raw_data
        self.uid = uid
        self.position = position
        self.run_pandoc = run_pandoc

        self.output_data = self.extract_keypoint()


    def extract_keypoint(self):
        """ Extracts the data from the keypoint syntax. """

        regex = r"keypoint\{(.*)\}"

        find = re.search(regex, self.raw_data, re.VERBOSE)

        try:
            output = find.group(1)
        except AttributeError:  # no match
            output = ""

        if self.run_pandoc:
            return self.pandoc_raw_data(output)
        else:
            return output


    def pandoc_raw_data(self, text):
        """ Runs pandoc (latex to markdown) on the extracted data string, text """

        return pypandoc.convert(text, "markdown", format="tex")



class Part(object):
    """ Basic class for the storage of sections, lectures, start and end points """

    def __init__(self, name, start, end, uid=""):
        self.name = name
        self.start = start
        self.end = end
        self.uid = uid

        return


class MasterData(object):
    """ Master data object, holds the following data:

        + Input string (text)
        + Lecture start and end points (lectures)
        + Section start and end points (sections)
        + Keypoints (keypoints)
        + Output string (output) """

    def __init__(self, text):
        self.text = ltcstm.regex.remove_pdfonly(text)
        self.lectures = []
        self.sections = []
        self.keypoints = []
        self.output = ""


    def find_start_stop(self, text, items):
        """ Returns a list of tuples that describe what line numbers the items run over.
        So, for example, if text is

        <x>
        blah
        s
        <y>
        ssd

        one would recieve [(0, 3), (3, 4)] """

        # We can assume that the items are ordered.

        return


    def get_lectures(self, text):
        """ Gets the list of lectures (as part objects). """
        lectures = ltcstm.regex.find_lectures(text)

        replaced, uids = ltcstm.regex.replace_with_uids(text, lectures, "LEC")







