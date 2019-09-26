import os

## splitsep

def splitSep(pathlist):
    """
    splits paths in pathlist into another list using os.sep as split point
    """
    i = -1
    for path in pathlist:
        i += 1
        pathlist[i] = path.split(os.sep)
    
    return pathlist