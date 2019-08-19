"""
Parse the files to determine the calling tree
"""
from __future__ import print_function
from utilities import treewalk
from parsers import FindDefinitions, ParseFile
from collections import OrderedDict

def Parse(directory, include_ext=[], exclude_dirs=[], verbose=False):
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
    verbose : bool, optional
        Print more status information to the screen
    """

    print("\nFinding Fortran files in = {}".format(directory))
    if (len(include_ext) > 0):
        print("\n\tincluding extensions:")
        for e in include_ext:
            print("\t\t{}".format(e))
    if (len(exclude_dirs) > 0):
        print("\n\texcluding directories:")
        for d in exclude_dirs:
            print("\t\t{}".format(d))
    files = treewalk(directory, include_ext=include_ext, exclude_dirs=exclude_dirs)

    if (len(files) < 1):
        print("\nERROR: found no matching files in {}\n".format(directory))
        return

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
    print("\nFinding function/subroutine definitions...")
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

    valid_function_names = functions + list(interfaces.keys()) + subroutines

    # re-read each file to get what calls each function/subroutine makes
    print("\nFinding calls to functions/subroutines...")
    for f in files:
        c, n = ParseFile(f, valid_function_names)
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

    # build the calling tree
    print("\nBuilding calling tree")
    call_hist = []; intr_hist = []
    print("\tmain program calls:")
    for k in calls[main_program_name]:
        kcall = k[0]
        ctype = k[1]
        hist = GetTree(kcall, calls, numcalls, [], warn=False)
        call_hist.append(hist)
        print("\t\t{} calls:".format(kcall))
        print("\t\t\t{}".format(hist))

    # write results to html file using a "collapsible"
    print()

def GetTree(fkey, calls, ncalls, call_history, warn=False):

    if (fkey in calls.keys()):

        if (ncalls[fkey] == 0): # no calls are made
            return call_history

        routine_calls = calls[fkey]

        for entry in routine_calls: # loop over all calls made by fkey
            newkey = entry[0]
            call_history.append(newkey)
            call_history = GetTree(newkey, calls, ncalls, call_history, warn=warn)
        return call_history
    else:
        print("ERROR: should never be here... key = \"{}\" was not found".format(fkey))
        return call_history

