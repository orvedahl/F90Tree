"""
F90Tree module interface

Usage:
    F90Tree [options] <source_directory>

Options:
    --ext=<e>       Comma separated list of file extensions [default: F90]
    --exclude=<d>   Comma separated list of directories to exclude
"""

if __name__ == "__main__":

    from __future__ import print_function
    from docopt import docopt
    from F90Tree import parse

    args = docopt(__doc__)

    directory = args["<source_directory>"]
    ext = args["--ext"].split(",")
    exclude = args["--exclude"]
    if (exclude is not None):
        exclude_dirs = exclude.split(",")
    else:
        exclude_dirs = []

    parse.Parse(directory, ext=ext, exclude_dirs=exclude_dirs)

