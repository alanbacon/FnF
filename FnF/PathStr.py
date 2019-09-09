import os
import stat
import re
from functools import reduce

import StringQuartet
from pyAbstracts import ComparableMixin

digitRE = re.compile('\d+')

def dedupConsecutiveElementsFromList(l, elementToDedup=''):
    nextEl = None
    for i in range(len(l)-1, -1, -1):
        el = l[i]
        if el == nextEl == elementToDedup:
            del l[i+1]
        nextEl = el


def findNextGroupOfElementsInList(l, elementToLookFor='..'):
    sliceStart = 0
    sliceEnd = 0
    inGroup = False
    for i, el in enumerate(l):
        if el == elementToLookFor:
            if not inGroup:
                sliceStart = i
                inGroup = True
        else:
            if inGroup:
                sliceEnd = i
                break

    return slice(sliceStart, sliceEnd)


def removeNListElementsBeforeIndex(l, numElsToRemove, beforeIndex, emptyEls=['.', '']):
    start = beforeIndex - 1
    end = -1
    for i in range(start, end, -1):
        if numElsToRemove == 0:
            break

        el = l[i]
        if not el in emptyEls:
            numElsToRemove -= 1
            del l[i]

    if numElsToRemove > 0:
        raise RuntimeError('overflow')


class PathStr(ComparableMixin, str):
    # must overload __new__ for immutable type because by the time __init__ is called
    # (i.e. after __new__) it is too late to
    # change any data
    def __new__(cls, *args, **kw):
        # allow creation from list of directories
        if isinstance(args[0], list):
            dedupConsecutiveElementsFromList(args[0])
            if len(args[0]) == 0:
                args = ('',) + args[1:]
            elif args[0][0] == '':
                args = (os.path.join(os.sep,*args[0]),) + args[1:]
            else:
                args = (os.path.join(*args[0]),) + args[1:]

        # cls = FnF.PathStr (a subtype of str)
        return str.__new__(cls, *args, **kw) # this call to new returns object of type cls (FnF.PathStr)
    
    # self = the return value of __new__  *args is the original unmodified *args from before when __new__ is called
    def __init__(self, *args):
        self.__path = ''
        self.__filename = ''
        self.__ext = ''
        self.sep = os.sep
        self.stat = None

        self._pathAsList = None
        if isinstance(args[0], list):
            self._pathAsList = args[0]

        # prepare data for use by __lt__
        # _lt_ may get called many times in a sort, __preplt__ will only get called
        # once per object
        self._lessThanPrepped = False
        # separate filename and extension
        # the return values will also be of type str (not PathStr)
        self.__path, File = os.path.split(self)
        self.__filename, self.__ext = os.path.splitext(File)
        self.raw = self.__str__()

    def getPathAsList(self, slashIndicators=True):
        if self._pathAsList is None:
            # split self string using path separator
            # cache the result, this will always be valid because this object is immutable
            if self.raw == '':
                self._pathAsList = []
            else:
                self._pathAsList = self.raw.split(self.sep)

            dedupConsecutiveElementsFromList(self._pathAsList)

        # get cached value
        pathlist = self._pathAsList

        if not slashIndicators:
            if pathlist[0] == '':
                startInd = 1
            else:
                startInd = 0

            if pathlist[-1] == '':
                endInd = -1
            else:
                endInd = len(pathlist)

            pathlist = pathlist[startInd:endInd]

        return pathlist

    def getParentFolder(self):
        pathAsList = self.getPathAsList()
        for i in range(len(pathAsList)-1, -1, -1):
            el = pathAsList[i]
            if not el == '':
                pathAsList[i] = ''
                break

        return PathStr(pathAsList)

    def getPathRelativeTo(self, otherPathStr, dotSlash=True):
        if not isinstance(otherPathStr, PathStr):
            otherPathStr = PathStr(otherPathStr)

        if not otherPathStr.ispathstyle:
            raise TypeError('paths must have a trailing slash')

        isSelfPathStyle = self.ispathstyle

        otherPathList = otherPathStr.getPathAsList()
        del otherPathList[-1]  # remove end slash marker
        selfPathList = self.getPathAsList()
        i = 0

        while True:
            i += 1
            if not selfPathList or not otherPathList:
                break

            if otherPathList[0] == selfPathList[0]:
                del otherPathList[0]
                del selfPathList[0]
            elif i==1:
                raise RuntimeError('relative paths can only be calculated from paths with a common root')
            else:
                break


        # however many directories left on otherPathList indicate how many levels to go up
        # add on whatever is left on selfPathList 
        numUpLevels = len(otherPathList)
        if numUpLevels > 0:
            relativePathList = ( ['..'] * numUpLevels ) + selfPathList
        else:
            if dotSlash:
                relativePathList = ['.']
            else:
                relativePathList = []
            relativePathList += selfPathList


        return PathStr(relativePathList)

    def _getStat(self):
        if not self.stat:
            try:
                self.stat = os.stat(self.raw)
            except FileNotFoundError:
                self.stat = 'no_exist'
        
    @property
    def path(self):                            # allow getting of private attribute
        path = self.__path
        if path in ['', self.sep]:
            return path
        else:
            return path + self.sep
        
    @property
    def filename(self):                        # allow getting of private attribute
        return self.__filename
        
    @property
    def ext(self):                             # allow getting of private attribute
        return self.__ext

    @property
    def exists(self):
        self._getStat()
        if self.stat == 'no_exist':
            return False
        else:
            return True

    @property
    def isdir(self):
        self._getStat()
        if self.stat == 'no_exist':
            return False
        else:
            return stat.S_ISDIR(self.stat[stat.ST_MODE])

    @property
    def ispathstyle(self):
        if self.raw == '':
            return False
        else:
            # if object.path is itself then it must have just been a path to begin with
            return self.path == self.raw

    @staticmethod
    def join(*pathStrs):
        for ps in pathStrs:
            if not isinstance(ps, PathStr):
                raise NotImplementedError('can only join together PathStr objects')

        newPathAsList = reduce(
            lambda a, b: 
                a + b.getPathAsList()
            ,
            pathStrs,
            []
        )
        
        # remove any '.' from the path, unless its the first part of the path
        newPathAsList = newPathAsList[0:1] + [el for el in newPathAsList[1:] if not el == '.']
        # remove any '' from the path, unless its the first or last part of the path
        newPathAsList = newPathAsList[0:1] + [el for el in newPathAsList[1:-1] if not el == ''] + newPathAsList[-1:]
        dotDotSlice = slice(0,1)
        while (dotDotSlice.stop - dotDotSlice.start) > 0:
            dotDotSlice = findNextGroupOfElementsInList(newPathAsList, elementToLookFor='..')
            del newPathAsList[dotDotSlice]
            try:
                removeNListElementsBeforeIndex(
                    newPathAsList,
                    dotDotSlice.stop - dotDotSlice.start,
                    dotDotSlice.start,
                    emptyEls=['.', '']
                )
            except RuntimeError:
                raise RuntimeError('too many "../", overflowed in front of path')
        return PathStr(newPathAsList)

    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if isinstance(other, str):
            return hash(self) == hash(other)
        else:
            raise NotImplementedError('PathStr object can only compare equality with other string like objects')
    
    def __ne__(self, other):
        return not (self == other)

    # wrapper for StripRegex
    # container for the different parts of a file string (path,file,ext), object used in sort
    class StrippedStr:
        def __init__(self, *args):
            # convert to lowercase (don't want to sort on case)
            self.raw = args[0].lower()
            # create a StripRegex object that will be able to strip out any digits from a string
            self.__StripRE = StringQuartet.StripRegex(digitRE)
            # use StripRegex obj to give a string with the numbers removed
            # a list of the numbers (in the order they appear) and there positions
            self.__StripRE.Strip(self.raw)
            
            self.parts = []
            for i, g in enumerate(self.__StripRE.allGroups):
                if i%2 == 0:
                    self.parts.append(g)
                else:
                    self.parts.append(int(g))

    def __preplt__(self):
        self.__StrippedFolders = []

        path = PathStr(self.path)
        filename = self.filename
        ext = self.ext
        pathAsList = path.getPathAsList()
        for f in pathAsList:
            self.__StrippedFolders.append(PathStr.StrippedStr(f))
        self.__StrippedFolders.append(PathStr.StrippedStr(filename))
        self.__StrippedFolders.append(PathStr.StrippedStr(ext))

        self._lessThanPrepped = True

    # make iterable containers (Lists,Tuples,Filename Class) of PathStr sortable:
    # define the less than function 
    # (other rich comparisons will be defined using the ComparableMixin class)    
    def __lt__(self, other):

        if not isinstance(other, PathStr):
            raise NotImplementedError('can only compare less than with other PathStr objects')

        if not self._lessThanPrepped:
            self.__preplt__()

        if not other._lessThanPrepped:
            other.__preplt__()

        self_ = self.__StrippedFolders
        other_ = other.__StrippedFolders

        for i, S_folder in enumerate(self_):
            if i >= len(other_):
                # other string has more folder depth
                return True

            O_folder = other_[i]
            for j, S_part in enumerate(S_folder.parts):
                if j >= len(O_folder.parts):
                    # other folder has longer name
                    return True

                O_part = O_folder.parts[j]
                if S_part == O_part:
                    # if this part of the foldername is the same they should be sorted
                    # on a more specific part of their foldername
                    continue
                elif S_part < O_part:
                    return True
                elif O_part < S_part:
                    return False
                else:
                    raise RuntimeError('unknown __lt__ algorithm failure')


        if len(other_) < len(self_):
            # self has more folder depth
            return False
        
        # the stripped strings were the same and the numbers contains in the unstripped string 
        # mathematically evaluate to be equivalent (they must contain padding zeros)
        # can only now compare the strings in the normal way
        return self.raw < other.raw

