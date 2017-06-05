""" Exposes config options """

import configparser
import sys


def read_config(filename='litm.cfg'):
    """ Reads the configuration options file and exposes key variables """

    config = configparser.ConfigParser()
    config.read(filename)

    read = {
        'compile_dir' : config.get('path', 'compile_dir'),
        'tex_dir' : config.get('path', 'tex_dir'),
        'image_dir' : config.get('path', 'image_dir'),
        'web_dir' : config.get('path', 'web_dir'),
        'args' : sys.argv,
        'own_files' : [f.strip() for f in config.get('path', 'own_files').split(',')],
    }

    return read
    