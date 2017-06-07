""" Contains regex replacement functions for each individual item """

import random
import re

import ltcstm.storage as store


def get_uid(prefix=""):
    """ Grabs a random unique identifier """
    return "{}{:0<10}".format(prefix, random.randint(0, 1e10))


def text_replace(text, initial, final):
    """ Recursive function to replace a list of initial in a string with another list """
    replaced = text.replace(initial[0], final[0])

    if len(initial) == 1:
        return replaced
    else:
        return text_replace(replaced, initial[1:], final[1:])


def replace_with_uids(text, items, prefix=""):
    """ Replaces the items list with UIDs with a prefix, i.e.
            "LEC<UID>"
        for LEC as prefix in the text string.abs

        Returns output, uid_list"""

    # generate the uids
    uid_list = [get_uid(prefix) for x in items]

    output = text_replace(text, items, uid_list)

    return output, uid_list


def find_items(text, regex):
    """ Quick wrapper over the regex module. Finds items that are associated with regex
        in text and returns them. """

    compiled = re.compile(regex, re.VERBOSE)

    return compiled.findall(text)


def find_lectures(text):
    """ Finds all instances of custom lecture syntax in the text string """

    regex = r"%%\\lecture{(.*)}"

    return find_items(text, regex)


def find_sections(text):
    """ Finds all instances of custom section syntax in the text string """

    regex = r"%%\\section{(.*)}"

    return find_items(text, regex)


def find_pdfonly(text):
    """ We can just kill the pdfonly blocks as they are not relevant to us. To do that, we'll
        iterate through the text string line by line and remove all references. """

    split = text.split("\n")

    pdfonly = False

    output = []

    for line in split:
        if line.contains(r"%%@pdfonly"):
            pdfonly = True

            continue

        elif line.contains(r"%%@pdfonlyend"):
            pdfonly = False

            continue
        
        elif pdfonly:  # pdfonly blocks are skipped here.
            continue

        else:
            output.append(line)

        return "\n".join(output)


