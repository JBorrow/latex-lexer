""" Lexer portion of the code from original compiler.py """

import ply.lex as lex

from ltcstm.helper import get_uid


TOKENS = (
    'KEY',
    'TEXT',
    'PDFONLYBEGIN',
    'PDFONLYEND',
)


def register(key, value, uid):
    """ Register function for ply lexer """

    for k, dic in [('keypoint', lexer.keypoints),
                   ('image', lexer.images),
                   ('question', lexer.questions)]:
        if key == k:
            if not lexer.current['section'] in dic.keys():
                dic[lexer.current['section']] = []
            if not lexer.current['lecture'] in dic.keys():
                dic[lexer.current['lecture']] = []
            dic[lexer.current['section']].append(value)
            dic[lexer.current['lecture']].append(value)
    if key in ['section', 'lecture']:
        lexer.begin[key][value] = uid
        lexer.end[key][lexer.current[key]] = uid
        lexer.current[key] = value
    if key == 'section':
        lexer.sections.append(value)
    if key == 'lecture':
        lexer.lectures.append(value)
    lexer.uids[key][value] = uid


def t_KEY(t):
    r'%%\\(?P<key>\w+)\{(?P<value>.*)\}'
    key = lexer.lexmatch.group('key')
    value = lexer.lexmatch.group('value')
    uid = get_uid()
    register(key, value, uid)
    t.value = (key, value, uid)
    return t


def t_PDFONLYBEGIN(t):
    r'%%@pdfonly(?P<txt>.*?)'
    t.value = ('PDFONLYBEGIN', lexer.lexmatch.group('txt'))
    return t


def t_PDFONLYEND(t):
    r'%%@endpdfonly'
    t.value = ('PDFONLYEND', lexer.lexmatch.group('txt'))
    return t


def t_TEXT(t):
    r'(?:(?:\\%)|(?:[^%\\]+)|(?:\\[^%])|(%[^%])|(?:%%[^\\@]))+'
    t.value = ('TEXT', t.value)

    return t


def p_blocks(p):
    'blocks : block blocks'
    #if the block is ignored the result is None
    if p[1]:
        p[0] = [p[1]]+p[2]
    else:
        p[0] = p[2]


def p_blocksnone(p):
    'blocks : '
    p[0] = []


def p_pdfonly(p):
    'PDFONLY : PDFONLYBEGIN blocks PDFONLYEND'
    p[0] = ('PDFONLY',p[2])


def p_block(p):
    '''block : TEXT
             | KEY
             | PDFONLY
    '''
    p[0] = p[1]


lexer = lex.lex()
