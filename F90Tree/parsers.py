"""
Define a bunch of classes to help in the parsing process
"""
from __future__ import print_function
import os
import re
from collections import OrderedDict

def FindDefinitions(filename, verbose=False):
    """
    Parse a Fortran file for function/subroutine definitions

    Args
    ----
    filename : string
        The filename of the Fortran source code to parse
    verbose : bool, optional
        Print more information to screen

    Returns
    -------
    funcnames : list
        List of function names that are defined in this file
    subnames : list
        List of subroutine names that are defined in this file
    interfaces : dict
        Dictionary holding the interface mappings. The key is the interface
        name and the values are the routines that the interface name could call
    definitions : dict
        Dictionary holding the routine mappings. The key is the callable
        function/subroutine name and the value is the filename that holds
        its definition
    contains_main : bool
        Indicates whether or not this file contains the main program
    main_name : str
        The name of the main program if it was found, None if it was not found
    """

    funcnames     = [] # list of function names
    subnames      = [] # list of subroutine names
    interfaces    = {} # maps the interface to the possible calling routines
    definitions   = {} # maps the routine name to the filename
    contains_main = False
    main_name     = None

    if (not os.path.isfile(filename)):
        print("ERROR: {} does not exist, skipping".format(filename))
        return

    # regular expressions for "end program", "end subroutine", and "end function"
    # (\s*) = 0 or more white space
    # (\s+) = 1 or more white space
    # (end) = "end"
    # ^     = start of the line
    # ((?:[a-z_][a-z_0-9]+)) = pretty much any fortran acceptable variable name
    #    ?: matches whatever follows, but cant be stored unless the entire re.compile()
    #       is set equal to something. This is more efficient than searching each time
    #    [a-z_] is any letter plus the underscore
    #    [a-z_0-9] is any letter, number, or underscore
    #    the following "+" results in 1 or more repetitions of what came before it
    #    | is logical OR
    #    DOTALL allows the "." character to include newlines, it usually doesn't
    sfunc = re.compile("(\s*)(function)(\s+)((?:[a-z_][a-z_0-9]+))(\s*)",
                        re.IGNORECASE|re.DOTALL)
    sprog = re.compile("(^\s*)(program)(\s+)((?:[a-z_][a-z_0-9]+))",
                        re.IGNORECASE|re.DOTALL)
    sintr = re.compile("(^\s*)(interface)(\s+)((?:[a-z_][a-z_0-9]+))",
                        re.IGNORECASE|re.DOTALL)
    ssubr = re.compile("(^\s*)(subroutine)(\s+)((?:[a-z_][a-z_0-9]+))(\s*)",
                        re.IGNORECASE|re.DOTALL)
    efunc = re.compile("(^\s*)(end)(\s+)(function)(\s+)((?:[a-z_][a-z_0-9]+))(\s*)",
                        re.IGNORECASE|re.DOTALL)
    eprog = re.compile("(^\s*)(end)(\s+)(program)(\s+)((?:[a-z_][a-z_0-9]+))",
                        re.IGNORECASE|re.DOTALL)
    eintr = re.compile("(^\s*)(end)(\s+)(interface)(\s+)((?:[a-z_][a-z_0-9]+))",
                        re.IGNORECASE|re.DOTALL)
    esubr = re.compile("(^\s*)(end)(\s+)(subroutine)(\s+)((?:[a-z_][a-z_0-9]+))",
                        re.IGNORECASE|re.DOTALL)
    modpr = re.compile("(^\s*)(module)(\s+)(procedure)(\s+)((?:[a-z_][a-z_0-9]+))",
                        re.IGNORECASE|re.DOTALL)
    paren = re.compile("(\s*)(\()", re.IGNORECASE|re.DOTALL)

    found_main = False
    start_interface = False

    if (verbose):
        print("\tparsing file = {}".format(filename))
    with open(filename, 'r') as mf:

        for _line in mf:

            line = _line.lower()

            if (line.lstrip().startswith("!")): continue # skip comments
            if (line.lstrip() == ""): continue           # skip empty lines

            i = line.find("!") # strip off any trailing comments. find returns -1
                               # if substring is not found, but -1 is a valid slice index
            if (i > 0):        # so protect against that.
                line = line[:i]

            ####################################
            # main program definition
            ####################################
            if (not found_main): # determine if this file contains the main program
                sprogram = sprog.search(line)
                eprogram = eprog.search(line)
                # re.search(line) returns if it is found and what the match is
                # group(i) returns the i-th parenthesized subgroup of the search pattern
                # for the sprogram:
                #     i=0 is whole thing
                #     i=1 is possible space
                #     i=2 is "program"
                #     i=3 is one or more spaces
                #     i=4 is the name
                if (sprogram and not(eprogram)): # ensure this is the beginning, not end
                    Pname = sprogram.group(4).strip()
                    main_name = Pname
                    funcnames.append(main_name)
                    contains_main = True
                    found_main = True
                    continue

            ####################################
            # interface blocks
            ####################################
            sinterface = sintr.search(line)
            einterface = eintr.search(line)
            par        = paren.search(line) # valid interface blocks should not have "("
            if (sinterface and not(einterface) and not(par)):
                start_interface = True
                Iname = sinterface.group(4).strip()
                interfaces[Iname] = []
                continue

            if (start_interface): # parse the interface stuff
                mod = modpr.search(line)
                if (mod):
                    i = line.find("procedure")                # modpr wont get the comma
                    names = line[i+len("procedure"):].strip() # separated list, do that
                    names = names.split(",")                  # manually
                    for n in names:
                        interfaces[Iname].append(n)
                    continue

            if (einterface and not(par)): # this is the end of a valid interface
                start_interface = False
                continue

            ####################################
            # function definitions
            ####################################
            sfunction = sfunc.search(line)
            efunction = efunc.search(line)
            if (sfunction and not(efunction)):
                Fname = sfunction.group(4).strip()
                funcnames.append(Fname)
                continue

            ####################################
            # subroutine definitions
            ####################################
            ssubroutine = ssubr.search(line)
            esubroutine = esubr.search(line)
            if (ssubroutine and not(esubroutine)):
                Sname = ssubroutine.group(4).strip()
                subnames.append(Sname)
                continue

    # finally, map the routine name to the filename
    for f in funcnames:
        definitions[f] = filename
    for s in subnames:
        definitions[s] = filename

    return funcnames, subnames, interfaces, definitions, contains_main, main_name

def ParseFile(filename, callable_names, verbose=False):
    """
    Parse a Fortran file to determine what routines each function/subroutine calls

    Args
    ----
    filename : string
        The filename of the Fortran source code to parse
    callable_names : list
        Global list of all suitable function/subroutine names, including interface names
    verbose : bool, optional
        Print more information to screen

    Returns
    -------
    calls : ordered dict
        Dictionary holding the routine mappings. The key is the callable
        function/subroutine name and the value is a list of routine calls
    numcalls : ordered dict
        Dictionary holding the routine mappings. The key is the callable
        function/subroutine name and the value is number of routine calls made
        by that function/subroutine
    """

    calls    = OrderedDict()
    numcalls = OrderedDict()

    sprogram = re.compile("(^\s*)(program)(\s+)((?:[a-z_][a-z_0-9]+))",
                          re.IGNORECASE|re.DOTALL)
    eprogram = re.compile("(^\s*)(end)(\s+)(program)(\s+)((?:[a-z_][a-z_0-9]+))",
                          re.IGNORECASE|re.DOTALL)
    sfuncdef = re.compile("(\s*)(function)(\s+)((?:[a-z_][a-z_0-9]+))(\s*)",
                          re.IGNORECASE|re.DOTALL)
    efuncdef = re.compile("(^\s*)(end)(\s+)(function)(\s+)((?:[a-z_][a-z_0-9]+))(\s*)",
                          re.IGNORECASE|re.DOTALL)
    ssubdef  = re.compile("(^\s*)(subroutine)(\s+)((?:[a-z_][a-z_0-9]+))(\s*)",
                          re.IGNORECASE|re.DOTALL)
    esubdef  = re.compile("(^\s*)(end)(\s+)(subroutine)(\s+)((?:[a-z_][a-z_0-9]+))(\s*)",
                          re.IGNORECASE|re.DOTALL)
    some_call = re.compile("(\s*)((?:[a-z_][a-z_0-9]+))(\s*)(\()", re.IGNORECASE|re.DOTALL)
    sub_call  = re.compile("(\s*)(call)(\s+)((?:[a-z_][a-z_0-9]+))(\s*)(\()",
                           re.IGNORECASE|re.DOTALL)

    start_parse = False

    if (verbose):
        print("\tparsing file = {}".format(filename))
    with open(filename, 'r') as mf:

        for _line in mf:

            line = _line.lower()

            if (line.lstrip().startswith("!")): continue # skip comments
            if (line.lstrip() == ""): continue           # skip empty lines

            i = line.find("!") # strip off any trailing comments. find returns -1
                               # if substring is not found, but -1 is a valid slice index
            if (i > 0):        # so protect against that.
                line = line[:i]

            sprog = sprogram.search(line) # is this the main program
            eprog = eprogram.search(line)
            if (sprog and not(eprog)):
                start_parse = True
                Cname = sprog.group(4).strip()
                if (Cname not in calls.keys()): # always include the main program
                    calls[Cname] = []
                continue
            if (eprog):
                start_parse = False
                continue

            sfunc = sfuncdef.search(line) # is this a function definition
            efunc = efuncdef.search(line)
            if (sfunc and not(efunc)):
                i = line.find("function")
                if ("'" in line[:i]): continue # these hopefully catch: "function 2"
                if ('"' in line[:i]): continue
                Cname = sfunc.group(4).strip()
                if (Cname not in calls.keys()):
                    if (Cname in callable_names): # only include if its considered callable
                        start_parse = True
                        calls[Cname] = []
                continue
            if (efunc):
                start_parse = False
                continue

            ssub = ssubdef.search(line) # is this a subroutine definition
            esub = esubdef.search(line)
            if (ssub and not(esub)):
                Cname = ssub.group(4).strip()
                if (Cname not in calls.keys()):
                    if (Cname in callable_names): # only include if its considered callable
                        start_parse = True
                        calls[Cname] = []
                continue
            if (esub):
                start_parse = False
                continue

            # catch a few odd instances: trailing "end" or "end function" or "end subroutine"
            if (line.strip() == "end"):
                start_parse = False
                continue
            l = line.split()
            if (l[0] == "end" and l[1] in ["function", "subroutine"]):
                start_parse = False
                continue

            if (start_parse):
                c = some_call.search(line) # this should catch subroutine & function calls
                if (c):                    # and a few unwanted array operations
                    s = sub_call.search(line)
                    if (s): # this is definitely a subroutine call
                        name = s.group(4).strip()
                        if (name in callable_names): # this is a valid subroutine call
                            calls[Cname].append([name, "s"])
                    else: # this could be a function call or an array operation
                        name = c.group(2).strip()
                        if (name in callable_names): # this is a valid function call
                            calls[Cname].append([name, "f"])
                continue

    # compute total number of calls in each routine
    for k in calls.keys():
        v = calls[k] # should be a list of [name, "c"] elements
        numcalls[k] = len(v)

    return calls, numcalls

