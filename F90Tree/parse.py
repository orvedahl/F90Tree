"""
Parse the files to determine the calling tree
"""
from __future__ import print_function
from utilities import treewalk
from collections import OrderedDict

def Parse(directory, include_ext=[], exclude_dirs=[]):

    files = treewalk(directory, include_ext=include_ext, exclude_dirs=exclude_dirs)

    in_program_name = None
    main_program_file = None
    functions   = [] # list of all function names
    subroutines = [] # list of all subroutine names
    interfaces  = {} # dictionary holding interface_name:[specific routines] pairs
    filenames   = {} # dictionary holding routine_name:filename pairs
    funcnames   = {} # dictionary holding filename:[routine_names] pairs
    calls       = {} # dictionary holding routine_name:[list of routine calls]
                     # where each value is actually a list of [name, calltype]
    numcalls    = {} # dictionary holding routine_name:number_of_calls
    filecalls   = {} # dictionary holding filename:dict("calls":calls, "ncalls":numcalls)

    # get global list of functions/subroutines/interfaces
    for f in files:
        fnames, snames, ints, defs, has_main, main = FindDefinitions(f)
        functions += fnames
        subroutines += snames
        interfaces.update(ints)
        filenames.update(defs)
        funcnames[f] = fnames
        if (has_main):
            main_program_name = main
            main_program_file = f

    valid_callables = functions + list(interfaces.keys())

    # re-read each file to get what calls each function/subroutine make
    for f in files:
        c, n = ParseFile(filename, valid_callables)
        filecalls[f] = {"calls":c, "ncalls":n}
        calls.update(c)
        numcalls.update(n)

    # put the main program file first
    files.remove(main_program_file)
    files.insert(0, main_program_file)

    for f in files:
        ncalls = filecalls[f]
        if (ncalls == 0):
            continue
        else:

    # in the main program
    #    -get list of calls
    #    for each call
    #        -get list of calls
    #        for each call
    #            -get list of calls
    #            ...
    #                ...
def GetTree(calls, ncalls):
    if (ncalls == 0):
        return
    else:
        return GetTree(calls, ncalls)

    # need routine that will
    #    1) get list of calls
    #    if no calls, return some code
    #    if there are calls, call this code on each call
    #
    #    prime for recurrsion...
    #
    # write results to html file using a "collapsible"

