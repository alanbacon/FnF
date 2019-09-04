## FnF (Files and Folders) Module

import os
import re
import FnF


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
    return FnF.Filenames(files)

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
    return FnF.Filenames(dirs)

    
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
    return FnF.Filenames(pathlist)
    
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
    
    return FnF.Filenames(filelist)
    
    # ---------- END -------------- #
