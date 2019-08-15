"""
Various utility functions
"""
import os

def treewalk(top_dir, include_ext=[], exclude_dirs=[]):
    """
    Walk a directory tree and return full path of all files that were found.

    Args
    ----
    top_dir : str
        The top directory where the search will begin
    include_ext : list, optional
        List of file extensions to include, e.g., to find
        all Fortran files `include_ext=["f90", "F90", "f", "F"]`
    exclude_dirs : list, optional

        List of directories to exclude during the search. For example, to
        exclude the `build` directory, `exclude_dirs=["build"]`

    Returns
    -------
    filelist : list
        The resulting list of filenames
    """
    if (len(include_ext) == 0):
        include_all_files = True
    else:
        include_all_files = False
        include_ext = tuple(include_ext)

    filelist = []
    for root, dirs, files in os.walk(top_dir):

        # remove the excluded directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        # only include the correct file extensions
        if (include_all_files):
            for f in files:
                _f = os.path.abspath(os.path.join(root, f))
                filelist.append(_f)
        else:
            for f in files:
                _f = os.path.abspath(os.path.join(root, f))
                if (_f.endswith(include_ext)):
                    filelist.append(_f)

    return filelist


