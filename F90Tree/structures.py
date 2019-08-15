"""
Define a bunch of classes to help in the parsing process
"""
from __future__ import print_function
import os
import re

class FortranFile():
    """
    A Fortran file containing source code to be parsed
    """
    def __init__(self, filename):

        self.filename = filename

        self.has_main = False # does this file contain the main program?
        self.main_name = None

        self.subroutines = [] # store list of functions/subroutines in this file
        self.functions = []

        self.interfaces = {}  # key = interface name, value = list of associated routines

    def Parse(self):

        if (not os.path.isfile(self.filename)):
            print("ERROR: {} does not exist, skipping".format(self.filename))
            return

        # regular expressions for "end program", "end subroutine", and "end function"
        # (\s*) = 0 or more white space
        # (\s+) = 1 or more white space
        # (end) = "end"
        # ((?:[a-z_][a-z_0-9]+)) = pretty much any fortran acceptable variable name
        #    ?: matches whatever follows, but cant be stored unless the entire re.compile()
        #       is set equal to something. This is more efficient than searching each time
        #    [a-z_] is any letter plus the underscore
        #    [a-z_0-9] is any letter, number, or underscore
        #    the following "+" results in 1 or more repetitions of what came before it
        #    | is logical OR
        #    DOTALL allows the "." character to include newlines, it usually doesn't
        sfunc = re.compile("(\s*)(function)(\s+)((?:[a-z_][a-z_0-9]+))(\s*)(()",
                          re.IGNORECASE|re.DOTALL)
        sprog = re.compile("(\s*)(program)(\s+)((?:[a-z_][a-z_0-9]+))",
                          re.IGNORECASE|re.DOTALL)
        sintr = re.compile("(\s*)(interface)(\s+)((?:[a-z_][a-z_0-9]+))",
                          re.IGNORECASE|re.DOTALL)
        ssubr = re.compile("(\s*)(subroutine)(\s+)((?:[a-z_][a-z_0-9]+))(\s*)(()",
                          re.IGNORECASE|re.DOTALL)
        efunc = re.compile("(\s*)(end)(\s+)(function)(\s+)((?:[a-z_][a-z_0-9]+))(\s*)(()",
                          re.IGNORECASE|re.DOTALL)
        eprog = re.compile("(\s*)(end)(\s+)(program)(\s+)((?:[a-z_][a-z_0-9]+))",
                          re.IGNORECASE|re.DOTALL)
        eintr = re.compile("(\s*)(end)(\s+)(interface)(\s+)((?:[a-z_][a-z_0-9]+))",
                          re.IGNORECASE|re.DOTALL)
        esubr = re.compile("(\s*)(end)(\s+)(subroutine)(\s+)((?:[a-z_][a-z_0-9]+))",
                          re.IGNORECASE|re.DOTALL)
        modpr = re.compile("(\s*)(module)(\s+)(procedure)(\s+)((?:[a-z_][a-z_0-9]+))",
                          re.IGNORECASE|re.DOTALL)

        found_main = False
        start_interface = False

        print("parsing file = {}".format(self.filename))
        with open(self.filename, 'r') as mf:

            for _line in mf:

                line = _line.lower()

                if (line.lstrip().startswith("!")): continue # skip comments
                if (line.lstrip() == ""): continue           # skip empty lines

                ####################################
                # main program
                ####################################
                if (not found_main): # determine if this file contains the main program
                    sprogram = sprog.search(line)
                    eprogram = eprog.search(line)
                    # re.search(line) returns if it is found and what the match is
                    # group(i) = the i-th parenthesized subgroup of the search pattern
                    #     i=0 is whole thing
                    #     i=1 is possible space
                    #     i=2 is function|program|subroutine
                    #     i=3 is one or more spaces
                    #     i=4 is the name
                    #     i=5 is possible space (functions/subroutines only)
                    #     i=6 is an opening parenthesis (functions/subroutines only)
                    if (sprogram and not(eprogram)): # this is the beginning, not end
                        Pname = program.group(4).strip()  # get the main program name
                        Pname = Pname.split("!")[0]       # strip off comments
                        self.main_name = Pname
                        self.has_main = True
                        found_main = True
                        continue

                ####################################
                # interface blocks
                ####################################
                sinterface = sintr.search(line) # find any interface blocks
                einterface = eintr.search(line)
                if (sinterface and not(einterface)):
                    start_interface = True
                    Iname = interface.group(4).strip() # get name of interface
                    Iname = Iname.split("!")[0]         # strip off any comments
                    self.interfaces[Iname] = []
                    continue

                if (start_interface): # parse the interface stuff
                    mod = modpr.search(line)
                    if (mod):
                        names = mod.group(6).strip() # get the names, strip off comments
                        names = names.split("!")[0]  # and separate into individual names
                        names = names.split(",")
                        for n in names:
                            self.interfaces[Iname].append(n)
                        continue

                if (einterface): # this is the end
                    start_interface = False
                    continue

                ####################################
                # functions
                ####################################
                sfunction = sfunc.search(line) # find any function definitions
                efunction = efunc.search(line)
                if (function and not(efunction)):
                    Fname = function.group(4).strip()    # get the function name
                    Fname = Fname.split("!")[0]          # strip off any comments
                    self.functions.append(Callable(Fname, self.filename, "func"))
                    continue

                ####################################
                # subroutines
                ####################################
                ssubroutine = ssubr.search(line) # find any subroutine definitions
                esubroutine = esubr.search(line)
                if (subroutine):
                    Sname = subroutine.group(4).strip()    # get the subroutine name
                    Sname = Sname.split("!")[0]             # strip off any comments
                    self.subroutines.append(Callable(Sname, self.filename, "sub"))
                    continue

class Callable():
    """
    A Fortran callable such as a function or subroutine
    """
    def __init__(self, name, filename, calltype):

        self.filename = filename # name of file that contains source code
        self.name = name         # name of the routine

        self.type = calltype # is this a function of a subroutine

        self.called_by = None # who called this thing
        self.calls = []       # store name of the routines that I call
        self.is_sub = []      # the call is to a subroutine if T, to a function if F

    def NumCalls(self):
        return len(self.calls)

    def Parse(self):

        if (self.type == "func"):
            ssearch = "(\s*)(function)(\s+)({})(\s*)(()".format(self.name)
            esearch = "(\s*)(end)(\s+)(function)(\s+)({})(\s*)(()".format(self.name)
        elif (self.type == "sub"):
            ssearch = "(\s*)(subroutine)(\s+)({})(\s*)(()".format(self.name)
            esearch = "(\s*)(end)(\s+)(subroutine)(\s+)({})(\s*)(()".format(self.name)
        start = re.compile(ssearch, re.IGNORECASE|re.DOTALL)
        end   = re.compile(esearch, re.IGNORECASE|re.DOTALL)

        with open(self.filename, 'r') as mf:

            for _line in mf:

                line = _line.lower()

                if (line.lstrip().startswith("!")): continue # skip comments
                if (line.lstrip() == ""): continue           # skip empty lines

                sparse = start.search(line)
                eparse = end.search(line)
                if (sparse and not(eparse)):
                    start_parse = True
                    continue

                if (eparse):
                    start_parse = False
                    break

                if (start_parse):

