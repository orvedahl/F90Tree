"""
F90Tree module interface

Usage:
    F90Tree [options]

Options:
    --debug    Run in debug mode [default: False]
"""

if __name__ == "__main__":

    from __future__ import print_function
    from docopt import docopt
    from F90Tree import parser

    args = docopt(__doc__)
    print(args)

