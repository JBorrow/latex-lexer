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


class PreprocessedData(object):
    """ Holds the data before processing. """
    def __init__(self, text):
        self.text = text
        rep, self.lectures, self.lecture_uids = self.replace_lectures(text)
        rep, self.sections, self.section_uids = self.replace_sections(rep)
        rep, self.keypoints, self.keypoint_uids = self.replace_keypoints(rep)
        self.output_text = rep

    def replace_lectures(self, text):
        """ Replaces lectures with appropriate uids. """
        lectures = ltcstm.regex.find_lectures(text)

        replaced, uids = ltcstm.regex.replace_with_uids(text, lectures, "LEC-")

        return replaced, lectures, uids


    def replace_sections(self, text):
        """ Replaces sections with appropriate uids. """
        sections = ltcstm.regex.find_sections(text)

        replaced, uids = ltcstm.regex.replace_with_uids(text, sections, "LEC-")

        return replaced, sections, uids


    def replace_keypoints(self, text):
        """ Replaces keypoints with appropriate uids. """
        keypoints = ltcstm.regex.find_keypoints(text)

        replaced, uids = ltcstm.regex.replace_with_uids(text, keypoints, "LEC-")

        return replaced, keypoints, uids


class MasterData(object):
    """ Master data object, holds the following data:

        + Input string (text)
        + Lecture start and end points (lectures)
        + Section start and end points (sections)
        + Keypoints (keypoints)
        + Output string (output) """

    def __init__(self, text):
        self.text = ltcstm.regex.remove_pdfonly(text)
        self.preprocessed = self.replace_run(text)
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

        list_of_lines = text.split("\n")
        line_numbers = []

        # This is really slow
        for match in items:
            for i, line in enumerate(list_of_lines):
                if match in line:
                    line_numbers.append(i)
                    break
                else:
                    continue

        line_numbers.append(len(list_of_lines) - 1)  # For the final section - it must end somewhere

        return [(line_numbers[i], line_numbers[i+1]) for i in range(len(line_numbers) - 1)]


    def replace_run(self, text):
        """ Does the initial replacement run with the PreprocessedData object """
        preprocessed = PreprocessedData(text)

        return preprocessed








