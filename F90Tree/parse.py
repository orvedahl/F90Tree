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
                     # where each element in the value is actually a list of [name, calltype]
    numcalls    = {} # dictionary holding routine_name:number_of_calls

    # get global list of functions/subroutines/interfaces
    for f in fortranfiles:
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

    for fname in functions:
        filename = filenames[fname]
        funcs    = funcnames[filename]
        c,n = ParseFile(filename, funcs, valid_callables)
        calls.update(c)
        numcalls.update(n)

    # try to use numcalls to determine how to build the tree

    # in the main program
    #    -get list of calls
    #    for each call
    #        -get list of calls
    #        for each call
    #            -get list of calls
    #            ...
    #                ...
    # need routine that will
    #    1) get list of calls
    #    if no calls, return some code
    #    if there are calls, call this code on each call
    #
    #    prime for recurrsion...
    #
    # write results to html file using a "collapsible"

