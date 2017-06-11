""" Contains the objects and data structures used in the processing of LaTeX
    documents, including the keypoints storage structure.

    Date Created: 2017-06-07
    Created By: Josh Borrow """


from typing import List

import re
import pypandoc

import ltcstm.regex


def html_output(uid):
    """ Formats the UID as a html comment ready for replacement in the main text
        after processing. """
    return "<!-- {} -->".format(uid)


def split_data(master_data):
    """ Splits the master_data object by lectures and sections

        Returns secs, lecs, keypoints."""

    #TODO WRITE TEST

    markdown = master_data.output_text.split("\n")
    lectures = master_data.lectures
    sections = master_data.sections
    keypoints = master_data.keypoints

    # lecs[name] = lectures.name
    # lecs[name][keypoints] = [associated indicies in keypoints]
    # lecs[name][data] = associated markdown


    def find_keypoints_section(keypoints, section):
        """ Find the keypoints that are associated with a section """
        output = []

        for i, keypoint in enumerate(keypoints):
            if keypoint.section == section:
                output.append(i)
            else:
                continue

        return output


    def find_keypoints_lecture(keypoints, lecture):
        """ Find the keypoints that are associated with a lecture """
        output = []

        for i, keypoint in enumerate(keypoints):
            if keypoint.lecture == lecture:
                output.append(i)
            else:
                continue

        return output


    def split_single(markdown, parts, keypoints, find_keypoints):
        """ find_keypoints is a callable that finds the keypoints associated with the parts """
        output = {}

        for item in parts:
            lines = markdown[item.start, item.end]

            name = item.name

            kps = find_keypoints(keypoints, item)

            output[name] = {
                "data": "\n".join(lines),
                "keypoints": kps
            }

        return output


    secs = split_single(markdown, sections, keypoints, find_keypoints_section)
    lecs = split_single(markdown, lectures, keypoints, find_keypoints_lecture)
    kps = [kp.output_data for kp in keypoints]

    return secs, lecs, kps


class Keypoint(object):
    """ Basic keypoint storage and extraction class.

        If run_pandoc is taken to be True, pandoc is ran on the internal text.

        Position should be given as the line number that the keypoint as found at. """

    def __init__(self, raw_data, uid, position, lecture=None, section=None, run_pandoc=False):
        self.raw_data = raw_data
        self.uid = uid
        self.html = html_output(uid)
        self.position = position

        self.lecture = lecture
        self.section = section

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
        self.html = html_output(uid)

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

        replaced, uids = ltcstm.regex.replace_with_uids(text, sections, "SEC-")

        return replaced, sections, uids


    def replace_keypoints(self, text):
        """ Replaces keypoints with appropriate uids. """
        keypoints = ltcstm.regex.find_keypoints(text)

        replaced, uids = ltcstm.regex.replace_with_uids(text, keypoints, "KEY-")

        return replaced, keypoints, uids


class PostprocessedData(object):
    """ The analogue of the above PreprocessedData for the PostprocessedData.
        Creates nicely formatted HTML versions of everything.

        Ensure that preprocessed is of type PreprocessedData """

    def __init__(self, pre, markdown):
        assert isinstance(pre, PreprocessedData)

        self.pre = pre
        self.markdown = markdown

        self.lectures = self.categorise_part(pre.lectures, pre.lecture_uids)
        self.sections = self.categorise_part(pre.sections, pre.section_uids)
        self.keypoints = self.categorise_keypoints(pre.keypoints, pre.keypoint_uids)

        self.output = self.replace_all(self.markdown)


    def find_locations(self, text, items):
        """ Finds the locations of items in text (i.e. their line number) """

        # We can assume that the items are ordered.

        list_of_lines = text.split("\n")
        number_of_lines = len(list_of_lines)
        line_numbers = []

        # This is really slow
        for match in items:
            for i, line in enumerate(list_of_lines):
                if match in line:
                    line_numbers.append(i)
                    break
                else:
                    continue

        return line_numbers, number_of_lines


    def find_start_stop(self, text, items):
        """ Returns a list of tuples that describe what line numbers the items run over.
        So, for example, if text is

        <x>
        blah
        s
        <y>
        ssd

        one would recieve [(0, 3), (3, 4)] """

        line_numbers, number_of_lines = self.find_locations(text, items)

        line_numbers.append(number_of_lines - 1)  # For the final section - it must end somewhere

        return [(line_numbers[i], line_numbers[i+1]) for i in range(len(line_numbers) - 1)]


    def categorise_part(self, parts, part_uids):
        """ Creates the part objects from the Part class """
        parts = []

        start_stop = self.find_start_stop(self.markdown, part_uids)

        for part, uid, (start, stop) in zip(parts, part_uids, start_stop):
            parts.append(
                Part(part, start, stop, uid)
            )

        return parts


    def find_associated(self, line_number: int, haystack: List[Part]) -> Part:
        """ Finds the assocaited object in the haystack (of Part objects) that is at line_number.
            This is used to find the lecture and section that each keypoint is associated with """

        for needle in haystack:
            if (needle.start < line_number) and (needle.end > line_number):
                return needle
            else:
                continue

        # Graceful fallback, we'll stick the keypoint/etc. on the last part.

        return haystack[-1]


    def categorise_keypoints(self, keypoints, keypoint_uids):
        """ Creates the keypoint objects from the Keypoint class """
        keypoints = []
        line_numbers = self.find_locations(self.markdown, keypoint_uids)

        for keypoint, uid, line_number in zip(keypoints, keypoint_uids, line_numbers):
            lecture = self.find_associated(line_number, self.lectures)
            section = self.find_associated(line_number, self.sections)

            keypoints.append(
                Keypoint(keypoint, uid, line_number, lecture, section)
            )

        return keypoints


    def replace_with_html(self, text, items):
        """ Replaces UIDs with HTML comments so they are not presented to the user """

        uids = []
        htmls = []

        for item in items:
            uids.append(item.uid)
            htmls.append(item.html)

        try:
            replaced = ltcstm.regex.text_replace(text, uids, htmls)
        except IndexError:  # No replacements to be made
            replaced = text

        return replaced


    def replace_all(self, text):
        """ Replace all section markers, lecture markers, keypoint markers with their
            respective HTML comments. """

        text = self.replace_with_html(text, self.lectures)
        text = self.replace_with_html(text, self.sections)
        text = self.replace_with_html(text, self.keypoints)

        return text


class MasterData(object):
    """ Master data object, holds the following data:

        + Input string (text)
        + Lecture start and end points (lectures)
        + Section start and end points (sections)
        + Keypoints (keypoints)
        + Output string (output) """

    def __init__(self, text, bib=""):
        self.input_text = text
        self.bib = bib

        postprocessed = self.run_compiler(text)

        self.lectures = postprocessed.lectures
        self.sections = postprocessed.sections
        self.keypoints = postprocessed.keypoints
        self.output_text = postprocessed.output


    def run_compiler(self, text):
        """ Does the initial replacement run with the PreprocessedData object """
        text = ltcstm.regex.remove_pdfonly(text)

        preprocessed = PreprocessedData(text)
        markdown = self.run_pandoc(preprocessed.output_text)
        postprocessed = PostprocessedData(preprocessed, markdown)

        return postprocessed


    def run_pandoc(self, text):
        """ Runs pandoc (LaTeX -> Markdown) on the text string """
        if self.bib:
            bib = ["--bibliography={}".format(self.bib)]
        else:
            bib = []

        extra_args = [
            "--mathjax",
            "-F",
            "pandoc-crossref",
            "-F",
            "pandoc-citeproc"] + bib

        print("Running Pandoc (MD -> HTML)")
        output_data = pypandoc.convert_text(text, "html", format="md", extra_args=extra_args)

        return output_data
