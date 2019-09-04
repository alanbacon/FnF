## 
# there is much less overhead if sorting with this function than using PathStr implicit sort methods
# this function does give different results to using the implicit sort of PathStr variables using the
# overloaded __lt__ method. 
# e.g.
# given two filenames:
#
# fn = ['filename.f',
#       'filename (1).f']
#
# __lt__ will sort based on: (this is a simplification)
#
# sortparam = [['filename',  ''  , None,  '',  '.f'],
#              ['filename',  ' (',    1,  ')', '.f']]
#                             ^
#                 empty string is before the space character in ACSII
#
# this will cause 'filename.f' to be sorted first
#
# the actual comparison in this case would be between:
# 
#               'filename'
#           and 'filename ()'
#
# the file extensions are only considered if no conclusions can be drawn from the filename
#
# however humansort will sort based on: (this is not a simplification)
#
# sortparam = [['filename.f'          ],
#              ['filename (', 1, ').f']]
#                        ^
#           ASCII space (32) is before ASCII dot (46)
#
# this will cause 'filename (1).f to be sorted first


def humansort(l):
    """ Sort the given list in the way that humans expect.
    """
    # function that converts text into a number if possible
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    # function that splits up a string into section that are either numeric or not
    #       then converts each section to a number if possible
    # returns a list where the members are either strings or ints
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]
    # sorts the list of strings (filenames) based on the how the split lists are sorted
    l.sort(key=alphanum_key)