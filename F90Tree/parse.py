"""
Parse the files to determine the calling tree
"""
from __future__ import print_function

def Parse():

    # find all files

    # for each file
    #    -determine who owns the main program
    #    -get list of function definitions
    #    -get list of subroutine definitions

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
    #    if there are calls, call this code again
