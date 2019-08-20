"""
Parse the files to determine the calling tree
"""
from __future__ import print_function
from utilities import treewalk
from parsers import FindDefinitions, ParseFile
from collections import OrderedDict
import numpy as np
import sys

def Parse(directory, include_ext=[], exclude_dirs=[], ignore=[],
          verbose=False, output=None, rec_limit=None):
    """
    Parse the source tree to get the calling tree

    Args
    ----
    directory : str
        Path to the directory that holds the source code
    include_ext : list, optional
        List of valid file extensions, ".f90" is equivalent to "f90"
    exclude_dirs : list, optional
        List of directories to exclude, e.g., "build" or "tmp"
    ignore : list, optional
        List of routine names to exclude, e.g., user defined print/write functions
    verbose : bool, optional
        Print more status information to the screen
    output : str, optional
        Write the resulting tree to the given filename
    rec_limit : int, optional
        Set the recursion depth limit
    """

    if (rec_limit is not None):
        print("\n\nWARNING: old recursion depth limit = {}, restting it to = {}\n".format(
              sys.getrecursionlimit(), rec_limit))
        sys.setrecursionlimit(int(rec_limit))

    print("\nFinding Fortran files under : {}".format(directory))
    if (len(include_ext) > 0):
        print("\n\tincluding extensions:")
        for e in include_ext:
            print("\t\t{}".format(e))
    if (len(exclude_dirs) > 0):
        print("\n\texcluding directories:")
        for d in exclude_dirs:
            print("\t\t{}".format(d))
    if (len(ignore) > 0):
        print("\n\texcluding some routines:")
        for d in ignore:
            print("\t\t{}".format(d))
    files = treewalk(directory, include_ext=include_ext, exclude_dirs=exclude_dirs)

    if (len(files) < 1):
        print("\nERROR: found no matching files in {}\n".format(directory))
        return
    print("\t\nFound {} files".format(len(files)))

    main_program_name = None
    main_program_file = None
    has_main          = False
    main              = None
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
    print("\nFinding all user-defined function/subroutine definitions...")
    for f in files:
        fnames, snames, ints, defs, has_main, main = FindDefinitions(f, verbose=verbose)
        functions += fnames
        subroutines += snames
        interfaces.update(ints)
        filenames.update(defs)
        funcnames[f] = fnames
        if (has_main):
            main_program_name = main
            main_program_file = f

    print("\n\tFound {} functions".format(len(functions)))
    print(  "\tFound {} subroutines".format(len(subroutines)))
    print(  "\tFound {} interfaces".format(len(interfaces.keys())))

    # only function/subroutine/interface calls that are considered valid
    # will be added to the "calls" and "numcalls" dictionaries
    valid_routine_names = functions + list(interfaces.keys()) + subroutines

    # remove the ignored names
    for name in ignore:
        if (name in valid_routine_names):
            valid_routine_names.remove(name)

    # re-read each file to get what calls each function/subroutine makes
    print("\nFinding calls to functions/subroutines...")
    for f in files:
        c, n = ParseFile(f, valid_routine_names, verbose=verbose)
        filecalls[f] = {"calls":c, "ncalls":n}
        calls.update(c)
        numcalls.update(n)

    if (verbose):
        for k in calls.keys():
            print("calls by {}:".format(k))
            for i,j in enumerate(calls[k]):
                if (j[0] in calls.keys()):
                    print("\t{}) {}".format(i+1, j[0]))
                else:
                    print("\t{}) {}, intrinsic".format(i+1, j[0]))

    v = numcalls.values()
    avg = np.mean(v)
    med = np.median(v)
    maximum = 0; maxfunc = ""
    for k in numcalls.keys():
        if (numcalls[k] > maximum):
            maxfunc = k
            maximum = numcalls[k]
    print("\n\tEach routine makes {:.2f} calls on average ({:.2f} median)".format(avg, med))
    print("\tThe most calls is {}, made by {} in {}".format(maximum, maxfunc,
                                                   filenames[maxfunc][len(directory):]))

    # add interfaces to the calls/numcalls dictionaries
    for k in interfaces.keys():
        calls[k] = []
        numcalls[k] = 0

    # build the calling tree
    print("\nBuilding calling tree")
    call_hist = []; intr_hist = []
    print("\tmain program calls:")
    for k in calls[main_program_name]:
        kcall = k[0]
        ctype = k[1]
        hist = GetTree(kcall, calls, numcalls, [])
        call_hist.append(hist)
        print("\t  {} calls:".format(kcall))
        if (numcalls[kcall] > 0):
            print("\t    {}".format(np.asarray(calls[kcall])[:,0]))
            print("\t      {}".format(hist))

    print()
    if (output is not None): # write results to file

        with open(output, 'w') as mf:
             mf.write("Main Program calls\n")
             for i,c in enumerate(calls[main_program_name]):
                 func = c[0]; ctype = c[1]
                 mf.write("\t{} calls:\n".format(func))
                 for j in calls[func]:
                     c1 = j[0]; c2 = j[1]
                     mf.write("\t\t{}\n".format(c1))
                     h = GetTree(c1, calls, numcalls, [])
                     for k,e in enumerate(h):
                         mf.write("\t\t\t"+k*"\t"+"{}\n".format(e))
             mf.write("\n")
             mf.write("Interfaces\n")
             for k in interfaces.keys():
                 mf.write("\t{}\n".format(k))
                 v = interfaces[k]
                 for i in v:
                     mf.write("\t\t{}\n".format(i))

        print("saved tree to file = {}\n".format(output))

def GetTree(fkey, calls, ncalls, call_history):

    if (fkey in calls.keys()):
        if (ncalls[fkey] == 0): # no calls are made
            return call_history

        for entry in calls[fkey]: # loop over all calls made by fkey
            newkey = entry[0]
            call_history.append(newkey) # global call history
            call_history = GetTree(newkey, calls, ncalls, call_history)

        return call_history

    else:
        print("ERROR: should never be here... key = \"{}\" was not found".format(fkey))
        return call_history

