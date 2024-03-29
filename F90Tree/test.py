"""
F90Tree module interface

Usage:
    F90Tree [options] <source_directory>

Options:
    --ext=<e>         Comma separated list of file extensions [default: F90]
    --exclude=<d>     Comma separated list of directories to exclude
    --verbose         Verbose [default: False]
    --output=<o>      Save results to file in html format
    --rec-limit=<r>   Set the recursion depth limit
    --ignore=<f>      Comma separated list of routine names to exclude
"""
from __future__ import print_function

if __name__ == "__main__":

    from docopt import docopt
    #from F90Tree import main
    import main

    args = docopt(__doc__)

    directory = args["<source_directory>"]
    ext = args["--ext"].split(",")
    exclude = args["--exclude"]
    if (exclude is not None):
        exclude_dirs = exclude.split(",")
    else:
        exclude_dirs = []
    ign = args["--ignore"]
    if (ign is not None):
        ignore = ign.split(",")
    else:
        ignore = []

    main.Parse(directory, include_ext=ext, exclude_dirs=exclude_dirs, ignore=ignore,
               verbose=args['--verbose'], output=args['--output'],
               rec_limit=args['--rec-limit'])

