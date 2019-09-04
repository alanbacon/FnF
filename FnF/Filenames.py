import FnF
from pyAbstracts import TypedList


class Filenames(TypedList):
    
    def __init__(self, *args):
        self._oktypes = FnF.PathStr       # the only allowed type in this container is the PathStr type
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
            v = FnF.PathStr(v)
        
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
