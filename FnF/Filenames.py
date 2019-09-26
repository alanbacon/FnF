import FnF
from pyAbstracts import TypedList


class Filenames(TypedList):
    
    def __init__(self, *args):
        # the only allowed type in this container is the PathStr type
        self._oktypes = FnF.PathStr
        self._list = list()
        if len(args) > 0:
            self.extend(args[0])
    
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
        r = 'Filenames(['
        for ps in self:
            r = r + "'" + ps + "', "
        r = r[:-2]
        r = r + '])'
        return r
    
    # function to convert a Filename object back into a list of strings
    def getStrList(self):
        l = []
        for PS in self._list:
            l.append(PS.raw)
        return l
        
    # override the check method to allow variables of type str to be converted into type PathStr
    # allow assignment of lists (as long as they just contain str or PathStr)
    def check(self, v):
        # allow strings: but convert to PathStr
        if isinstance(v, str):
            v = FnF.PathStr(v)
        
        # allow $_oktypes i.e. PathStr's            
        if not isinstance(v, self._oktypes):
            raise TypeError('can only contain variables of type: ' + str(self._oktypes))
            
        return v
