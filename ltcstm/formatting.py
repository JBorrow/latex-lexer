""" Formatting functions for various markdown to HTML conversions """

import pypandoc


def insert_lecture_divs(orig_txt, lexer):
    """ Replaces the appropriate UIDS with formatted lecture divs """
    txt = str(orig_txt)
    for i, uid in lexer.uids['lecture'].items():
        comment = r"<!-- {} -->".format(uid)
        div = '''
<div id="lecture-{i}" class="lecture">
  <hr>Lecture {i}
</div>
        '''.format(i=i)

        txt = txt.replace(comment, div)

    return txt


def format_classes(classes):
    return ' '.join(classes)


def get_key_points_html(key, lexer, extra_class=[]):
    """ Gets the keypoints HTML """
    classes = format_classes(extra_class + ['keypoints'])
    if key not in lexer.keypoints.keys():
        return ''
    else:
        txt = '<div class="{}">\n<h2>\nKey Points\n</h2>'.format(classes)
        for keypt in lexer.keypoints[key]:
            div = '''<div class="key-point">{kptxt}</div>'''.format(
                kptxt=pypandoc.convert(keypt, 'html', format='tex')
            )
            txt += div
        txt += '</div>'

        return txt
