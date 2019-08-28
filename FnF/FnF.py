## FnF (Files and Folders) Module

import os
import sys
import stat
import StringQuartet
import re


## Filenames class (and the PathStr class)

from pyAbstracts import TypedList, ComparableMixin

#sepRE = re.compile(os.sep)
digitRE = re.compile('\d+')

class PathStr(ComparableMixin, str):
    
    # wrapper for StripRegex
    # container for the different parts of a file string (path,file,ext), object used in sort
    class StrippedStr(ComparableMixin):
        def __init__(self, *args):
            # convert to lowercase (don't want to sort on case)
            self.raw = args[0].lower()
            # create a StripRegex object that will be able to strip out any digits from a string
            self.__StripRE = StringQuartet.StripRegex(digitRE)
            # use StripRegex obj to give a string with the numbers removed
            # a list of the numbers (in the order they appear) and there positions
            self.__StripRE.Strip(self.raw)
            
            # expose the few attributes of the StripRegex class that we need for the __lt__ routine
            self.Stripped = self.__StripRE.StrippedString
            self.groups = self.__StripRE.groups
            self.NumGroups = self.__StripRE.NumGroups
            self.InsertLocations = self.__StripRE.InsertLocations
    
    # must overload __new__ for immutable type because by the time __init__ is called
    # (i.e. after __new__) it is too late to
    # change any data
    def __new__(cls, *args, **kw):
        # allow creation from list of directories
        if isinstance(args[0], list):
            if args[0][0] == '.':
                args = (os.path.join(*args[0]),) + args[1:]
            else:
                args = (os.path.join(os.sep,*args[0]),) + args[1:]

        # cls = FnF.PathStr (a subtype of str)
        return str.__new__(cls, *args, **kw) # this call to new returns object of type cls (FnF.PathStr)
    
    # self = the return value of __new__  *args is the orginal unmodified *args from before when __new__ is called
    def __init__(self, *args):
        self.__path = ''
        self.__filename = ''
        self.__ext = ''
        self.sep = os.sep
        #self.sepRE = sepRE
        self.stat = None


        self._pathAsList = None
        if isinstance(args[0], list):
            # then we already know what the path as list is
            # self._pathAsList will not have empty values at the start or end of it's 
            # array even if self.raw starts or ends with a slash.
            pathAsList = []
            ignore = True
            lastNonEmptyVal = None
            numIgnoredVals = 0
            for i, val in enumerate(args[0]):
                if ignore and val == '':
                    numIgnoredVals += 1
                    continue
                elif val != '':
                    ignore = False
                    lastNonEmptyVal = i
                pathAsList.append(val)
            del pathAsList[lastNonEmptyVal-numIgnoredVals+1:] # delete any empty values at the end of the list

            self._pathAsList = pathAsList

        # prepare data for use by __lt__
        # _lt_ may get called many times in a sort, __preplt__ will only get called
        # once per object
        self._lessThanPrepped = False
        # separate filename and extension
        # the return values will also be of type str (not PathStr)
        self.__path, File = os.path.split(self)
        self.__filename, self.__ext = os.path.splitext(File)
        self.raw = self.__str__()
    
    def __preplt__(self):

        self.__StrippedParts = []
        self.__StrippedParts.append(PathStr.StrippedStr(self.__path))
        self.__StrippedParts.append(PathStr.StrippedStr(self.__filename))
        self.__StrippedParts.append(PathStr.StrippedStr(self.__ext))
        self._lessThanPrepped = True

    def getPathAsList(self):
        if self._pathAsList is not None:
            # return cached value
            return self._pathAsList[:]

        # split self string using path seperator
        selfString = self.raw
        # remove any slashes that the string starts or ends with
        if selfString[0] == self.sep:
            selfString = selfString[1:]
        if selfString[-1] == self.sep:
            selfString = selfString[:-1]

        # cache the result, this will always be valid because this object is immutable
        #self._pathAsList = self.sepRE.split(selfString) # this appears to be slower than the manual method below
        self._pathAsList = []
        lastNonSlashInd = 0
        for c, char in enumerate(selfString):
            if char == self.sep:
                self._pathAsList.append(selfString[lastNonSlashInd:c])
                lastNonSlashInd = c+1
        self._pathAsList.append(selfString[lastNonSlashInd:c+1])

        return self._pathAsList[:]

    def getParentFolder(self):
        pathAsList = self.getPathAsList()
        pathAsList[-1] = ''
        return PathStr(pathAsList)

    def getPathRelativeTo(self, otherPathStr):
        if not isinstance(otherPathStr, PathStr):
            otherPathStr = PathStr(otherPathStr)

        if not otherPathStr.ispathstyle:
            raise TypeError('paths must have a trailing slash')

        isSelfPathStyle = self.ispathstyle

        otherPathList = otherPathStr.getPathAsList()
        selfPathList = self.getPathAsList()
        i = 0

        while True:
            i += 1
            if not selfPathList or not otherPathList:
                break

            if otherPathList[0] == selfPathList[0]:
                del otherPathList[0]
                del selfPathList[0]
            elif i==0:
                raise RuntimeError('relative paths can only be calculated from paths with a common root')
            else:
                break

        # however many directories left on otherPathList indicate how many levels to go up
        # add on whatever is left on selfPathList 
        numUpLevels = len(otherPathList)
        if numUpLevels > 0:
            relativePathList = ( ['..'] * numUpLevels ) + selfPathList
        else:
            relativePathList = ['.'] + selfPathList

        if isSelfPathStyle:
            relativePathList += ['']

        return PathStr(relativePathList)

    def _getStat(self):
        if not self.stat:
            try:
                self.stat = os.stat(self.raw)
            except FileNotFoundError:
                self.stat = 'no_exist'
        
    @property
    def path(self):                            # allow getting of private attribute
        return self.__path + self.sep
        
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
        # if object.path is itself then it must have just been a path to begin with
        return self.path == self.raw


    def __hash__(self):
        return hash(str(self))

    def __eq__(self, other):
        if isinstance(other, str):
            return hash(self) == hash(other)
        else:
            raise NotImplementedError('PathStr object can only compare equality with other string like objects')
    
    def __ne__(self, other):
        return not (self == other)

    # make iterable containers (Lists,Tuples,Filename Class) of PathStr sortable:
    # define the less than function 
    # (other rich comparisons will be defined using the ComparableMixin class)    
    def __lt__(self, other):

        if not self._lessThanPrepped:
            self.__preplt__()

        if not other._lessThanPrepped:
            other.__preplt__()

        # self and other are a list of length 3 of type StrippedStr
        # the path, the filename and the extension
        self_ = self.__StrippedParts
        other_ = other.__StrippedParts

        for i in range(3):
            S = self_[i]
            O = other_[i]
            if S.raw == O.raw:
                # if this part of the full filename is the same they should be sorted
                # on a more specific part of their filename
                continue
            elif S.Stripped == O.Stripped:
                # this part of the filename is only the same when the numbers have been stripped out
                for i, NumStr in enumerate(S.groups):
                    if i < O.NumGroups:
                        if S.InsertLocations[i] == O.InsertLocations[i]:
                            # self and other have numerics appearing in the same place
                            sNum = float(NumStr)
                            oNum = float(O.groups[i])
                            if sNum == oNum:
                                # have found the same number appearing at the same point
                                # can't make any conclusions on this
                                continue
                            else:
                                # have found two different numbers that occur at the same point
                                return sNum < oNum
                        else:
                            # self and other have numerics appearing in different places
                            # the string where the number appears first is the lesser string
                            return S.InsertLocations[i] < O.InsertLocations[i]
                    else:
                        # other is a longer string, and all numbers have been equal
                        return True
            # BUG------------------------------BUG---------------------BUG--------------------BUG-------------------BUG------------------------------
            #### just because this part of the filename isn't the same can't compare them as we don't know where the numbers have been stripped from
            #### use 'wallpaper-266390[1]' and 'wallpaper-2656946' as examples
            else: 
                # this part of the filename is not the same
                # can sort using the raw strings:
                return S.raw < O.raw
        
        # the stripped strings were the same and the numbers contains in the unstripped string 
        # mathematically evaluate to be equivalent (they must contain padding zeros)
        # can only now compare the strings in the normal way
        return self.raw < other.raw

    @staticmethod
    def join(*args):
        newPathList = []
        for ps in args:
            if not isinstance(ps, PathStr):
                ps = PathStr(ps)

            l = ps.getPathAsList()
            if len(newPathList) > 0 and l[0] == '.':
                l = l[1:]

            newPathList.extend(l)

        if args[-1].ispathstyle:
            newPathList.append('')

        return PathStr(newPathList)

#------------------------------------


class Filenames(TypedList):
    
    def __init__(self, *args):
        self._oktypes = PathStr             # the only allowed type in this container is the PathStr type
        self._list = list()
        self.RecursionGuard = False
        if len(args) > 0:
            self.extend(args[0])
    
    # this method is already overloaded in the TypedList abstract class but 
    def __getitem__(self, i): 
        val = self._list[i]
        if type(i) is slice:
            val = Filenames(val)
        return val
    
    # called by print        
    def __str__(self):
        s = ''
        # each entry is followed by a comma and a new line
        for v in self._list:
            s = s + v + ',\n'
        # remove the final new line character
        s = s[:-2]
        return s
    
    # called by just typing the object name into the terminal    
    def __repr__(self):
        r = 'Filenames([\n'
        r = r + self.__str__()
        r = r + '\n])'
        return r
    
    # function to convert a Filename object back into a list of strings
    def getstrlist(self):
        l = []
        for PS in self._list:
            l.append(PS.raw)
        return l
        
    # override the check method to allow variables of type str to be converted into type PathStr
    # allow assignment of lists (as long as they just contain str or PathStr)
    def check(self, v):
        # allow strings: but convert to PathStr
        if isinstance(v, str):
            v = PathStr(v)
        
        #     
        elif isinstance(v, list) and not self.RecursionGuard:
            # create a new list that just contains PathStr (if possible otherwise will error)
            self.RecursionGuard = True
            v = [self.check(i) for i in v]  # could also use enumerate instead of a list comprehension
            self.RecursionGuard = False
        
        # allow $_oktypes i.e. PathStr's            
        elif not isinstance(v, self._oktypes):
            raise TypeError(['can only contain variables of type: ', self._oktypes])
            
        return v


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
    return sorted(l, key=alphanum_key)

## listfiles


def listfiles(*args, **kwargs):
    """*args:   root_folder/[os.getcwd()]

    **kwargs:   full = True/False  [rec]    return a full path to the file (default value depends on $rec)
    
    Return a list of all file contained within a folder (not recursive)
    """

    # check arguments
    # fullpath?
    full = False
    if 'full' in kwargs:
        full = kwargs.pop('full')
    
    # set top level folder (either from input or use default)
    if len(args) == 1:
        root = args[0]  # from first input
    else:
        root = os.getcwd()  # default
    
    # get all files and folders, only put them in the list if they are are a file
    files = [f for f in os.listdir(root) if os.path.isfile(os.path.join(root, f))]  # list comprehension

    if full:
        for i, f in enumerate(files):
            files[i] = os.path.join(root, f)

    # convert list into a Filenames object
    # pass back list of files
    return Filenames(files)

## listsubdir


def listsubdir(*args, **kwargs):
    """*args:   root_folder/[os.getcwd()]

    **kwargs:   full = True/False     return a full path to the file
    
    Returns a list of all subfolders (not recursive)
    """

    # check arguments
    # fullpath?
    full = False
    if 'full' in kwargs:
        full = kwargs.pop('full')

    # end check arguments
    
    # set top level folder (either from input or use default)
    if len(args) == 1:
        root = args[0]  # from first input
    else:
        root = os.getcwd()  # default
    
    # get all files and folders, only put them in the list if they are a folder    
    dirs = [os.path.join(f,'') for f in os.listdir(root) if os.path.isdir(os.path.join(root, f))]  # list comprehension

    if full:
        for i, d in enumerate(dirs):
            dirs[i] = os.path.join(root, d)
    
    # convert list into a Filenames object
    # pass back list of sub folders
    return Filenames(dirs)
    
## splitsep


def splitsep(pathlist):
    """
    splits paths in pathlist into another list using os.sep as split point
    """
    i = -1
    for path in pathlist:
        i += 1
        pathlist[i] = path.split(os.sep)
    
    return pathlist
    
    
## listsubdirrec

def listsubdirrec(*args, **kwargs):
    """ 
    *args:      root_folder/[os.getcwd()]   top folder to recurse from
    
    **kwargs:   inc = []                  strings that must be in the paths
                dinc = []                 strings that must not be in the paths
                system = True/[False]     include system paths (if false adds '/.' and '/_' to dinc)
    
    Returns a recursive list of all subfolders
    """
    
    # ---- GET INPUTS ----- #
    
    # set top level folder (either from input or use default)
    if len(args) == 1:
        root = args[0]  # from first input
    else:
        root = os.getcwd()  # default
    
    # split
    if 'split' in kwargs:
        split = kwargs['split']
    else:
        split = False

    # inc(lude)
    inc = []
    if 'inc' in kwargs:
        # for each seperate string in $kwargs['inc'] append that string to the inc list
        # check that entries in $kwargs['inc'] are actually strings
        for s in kwargs['inc']:
            if type(s) is str:
                inc.append(s)
            else:
                raise Exception("inc must be a list of strings")

    # d(ont)inc(lude)
    dinc = []
    if 'dinc' in kwargs:
        # for each seperate string in$ kwargs['dinc'] append that string to the dinc list
        # check that entries in $kwargs['dinc'] are actually strings
        for s in kwargs['dinc']:
            if type(s) is str:
                dinc.append(s)
            else:
                raise Exception("dinc must be a list of strings")
        
    # system (folders)
    # if $system is false add '/.' and '/_' to the $dinc list
    if 'system' in kwargs:
        system = kwargs['system']
    else:
        system = False
        
    sep = os.sep
    dot = (sep + '.')
    underscore = (sep + '_')
    
    if not system:
        if dot not in dinc:
            dinc.append(dot)
        if underscore not in dinc:
            dinc.append(underscore)
    
    # -------- BEGIN --------- #
    
    pathlist = []
    
    # add each sub folder of the root (and the root its self to the path)
    for folder, subfolders, files in os.walk(root):
        # only add folders that meet the $inc and $dinc conditions 
        OK = True 
        
        for incStr in inc:
            if incStr not in folder:
                OK = False
            
        for dincStr in dinc:
            if dincStr in folder:
                OK = False
            
        if OK:
            pathlist.append(os.path.join(folder, ''))
    
    # pass back list of sub folders
    return Filenames(pathlist)
    
    # ---------- END -------------- #
    
## listfilesext


def listfilesext(*args, **kwargs):
    """
    *args:      root_folder/[os.getcwd()]   top folder to recurse from
    
    **kwargs:   ext = []                    list of file extention to include (i.e. ['.jpg','.bmp'])  
                rec = True/[False]          recursively look in all sub directorys
                full = True/False  [rec]    return a full path to the file (default value depends on $rec)
                
                --listsubdirrec opts.-- used if recursive option is selected
                
                system = True/[False]       include system paths (folders that start with /. or /_)
                inc = []                    strings that must be in the paths
                dinc = []                   strings that must not be in the paths
                     
    
    Returns a list of all files with the specified extentions (optionally recursive)
    """
    
    # -------- GET INPUTS ---------- #
    
    # set top level folder (either from input or use default)
    if len(args) == 1:
        root = args[0]  # from first input
    else:
        root = os.getcwd()  # default
    
    # what extentions to include
    ext = []  # default (all extenstions)
    if 'ext' in kwargs:
        ext = kwargs.pop('ext')
    
    ext = [e.lower() for e in ext]  # make ext all lower case
        
    if not ext:        # True if ext list is empty
        allext = True
    else:
        allext = False
    
    # recursive?
    rec = False
    if 'rec' in kwargs:
        rec = kwargs.pop('rec')
    
    # fullpath?
    full = rec
    if 'full' in kwargs:
        full = kwargs.pop('full')

    # these kwargs should be passed forward to listsubdirrec as well
    
    # inc(lude)
    inc = []    
    if 'inc' in kwargs:
        # for each seperate string in $kwargs['inc'] append that string to the inc list
        # check that entries in $kwargs['inc'] are actually strings
        for s in kwargs['inc']:
            if type(s) is str:
                inc.append(s)
            else:
                raise Exception("inc must be a list of strings")
        
    # d(ont)inc(lude)
    dinc = []    
    if 'dinc' in kwargs:
        # for each seperate string in$ kwargs['dinc'] append that string to the dinc list
        # check that entries in $kwargs['dinc'] are actually strings
        for s in kwargs['dinc']:
            if type(s) is str:
                dinc.append(s)
            else:
                raise Exception("dinc must be a list of strings")
        
    # system (folders)
    # if $system is false add '/.' and '/_' to the $dinc list
    if 'system' in kwargs:
        system = kwargs['system']
    else:
        system = False
        
    sep = os.sep
    dot = (sep + '.')
    underscore = (sep + '_')
    
    if not system:
        if dot not in dinc:
            dinc.append(dot)
        if underscore not in dinc:
            dinc.append(underscore)
    
    # --------- BEGIN ------------- #
    
    # --get folders to look for files in, either just root, or all recursive folders
    
    if rec:
        # get list of folders of recursively, pass forward any unused $kwargs
        folderlist = listsubdirrec(root, **kwargs)
    else:
        # or just use root folder
        folderlist = [root]
    
    # --end get folders
    
    # --get files and add to filelist if they have the right extention
    
    filelist = []
    for folder in folderlist:
        
        # output fullpath? create fullpath, prefix for this folder
        if full:
            CurrPath = folder
        else:
            CurrPath = ''
        
        # for each folder get the files within
        filelist_sub = listfiles(folder)
        
        for File in filelist_sub:
            # for each file only use ones that have the required extentions
            _, fext = os.path.splitext(File)
            if (fext.lower() in ext) or allext:
                # only add files that meet the $inc and $dinc conditions 
                OK = True 
                for incStr in inc:
                    if incStr not in (sep + File):
                        OK = False
                    
                for dincStr in dinc:
                    if dincStr in (sep + File):
                        OK = False
                    
                if OK:
                    file_full = os.path.join(CurrPath, File)
                    filelist.append(file_full)
    
    # -- end add to filelist    
    
    return Filenames(filelist)
    
    # ---------- END -------------- #
    
    
## 

## unit tests (turns out there is a module that is better for defining unit tests)

if __name__ == '__main__':
    
    # # listfiles
    # filelist = listfiles()
    # for f in filelist:
    #     print(f)
    
    # # listsubdir
    # folderlist = listsubdir()
    # for f in folderlist:
    #     print(f)
    
    # # listsubdirrec
    # folderlistrec = listsubdirrec
    # #for f in folderlistrec:
    # #    print(f)

    # loc = r'/Users/Airica/Downloads/'
    # F = listfiles(loc)
    # F = Filenames(F)
    # F.sort()
    
    loc = r'/Users/alanb/'
    P = listfilesext(loc, rec=False, system=True)
    P.sort()
    print(P)
