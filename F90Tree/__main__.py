"""
F90Tree module interface

Usage:
    python -m F90Tree [options] <source_directory>

Options:
    --ext=<e>       Comma separated list of file extensions [default: F90]
    --exclude=<d>   Comma separated list of directories to exclude
"""
from __future__ import print_function

if __name__ == "__main__":

    from docopt import docopt
    #from F90Tree import main
    import main

    args = docopt(__doc__)
    print(args)

    directory = args["<source_directory>"]
    ext = args["--ext"].split(",")
    exclude = args["--exclude"]
    if (exclude is not None):
        exclude_dirs = exclude.split(",")
    else:
        exclude_dirs = []

    print(directory)
    print(ext)
    print(exclude_dirs)
    main.Parse(directory, ext=ext, exclude_dirs=exclude_dirs)

