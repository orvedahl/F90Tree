"""
setup file
"""
from __future__ import print_function
import datetime
import setuptools
from distutils.core import setup
import sys
import os
import os.path as osp
if (sys.version_info[0] == 2):
    from ConfigParser import ConfigParser
else:
    from configparser import ConfigParser

def readme(filename='README'):
    """
    read the entire file and return the text
    """
    with open(filename, 'r') as f:
        text=f.read()
    return text

def run_setup():
    # make sure the environment variable was set
    if ("F90TreeDir" not in os.environ):
        print("\n\n---ERROR: F90TreeDir environment variable not set\n\n")
        print("In a BASH shell:")
        print("\texport F90TreeDir=/path/to/F90Tree")
        print("\n\tit is best to add this line to the ~/.bashrc file in order")
        print("\tto avoid having to do this every time a new shell is opened\n")
        print("In a C shell:")
        print("\tsetenv F90TreeDir /path/to/F90Tree")
        print("\n\tit is best to add this line to the ~/.cshrc file in order")
        print("\tto avoid having to do this every time a new shell is opened\n")
        sys.exit("failed to complete install process\n")

    # set version
    MAJOR = 0
    MINOR = 9
    MICRO = 0
    VERSION = '%d.%d.%d' % (MAJOR, MINOR, MICRO)

    # find all the package directories
    PACKAGES=setuptools.find_packages()

    # specify packages that F90Tree requires
    INSTALL_REQUIRES=["docopt", "numpy"]

    # various other package descriptors
    NAME = "F90Tree"
    DESCRIPTION = "Parse Fortran source code for the calling tree"
    AUTHOR = "Ryan J. Orvedahl"
    EMAIL= "ryan.orvedahl@gmail.com"
    LICENSE = "GNU General Public License v3 or later (GPLv3+)"

    # store all setup options
    setup_options = {}
    setup_options['name']             = NAME
    setup_options['author']           = AUTHOR
    setup_options['author_email']     = EMAIL
    setup_options['description']      = DESCRIPTION
    setup_options['long_description'] = readme()
    setup_options['license']          = LICENSE
    setup_options['version']          = VERSION
    setup_options['packages']         = PACKAGES
    setup_options['install_requires'] = INSTALL_REQUIRES

    # call setup script
    setup(**setup_options)

    install_directory = osp.dirname(osp.abspath(__file__))
    current_time = datetime.datetime.now()
    build_time = current_time.strftime("%Y-%m-%d %H:%M")

    # write various installation config options to file
    section = "installed-options"
    newconfig = ConfigParser()
    newconfig.add_section(section)
    python_version = [str(s) for s in sys.version_info[:3]]
    python_version = ".".join(python_version)
    newconfig.set(section, "python_version", python_version)
    newconfig.set(section, "install_directory", install_directory)
    newconfig.set(section, "build_time", build_time)

    newconfig.set(section, "version", VERSION)
    newconfig.set(section, "name", NAME)
    newconfig.set(section, "author", AUTHOR)
    newconfig.set(section, "description", DESCRIPTION)

    if (sys.version_info[0] == 2):
        installed_opts_cfg = "__installed_options_py2.cfg"
    else:
        installed_opts_cfg = "__installed_options_py3.cfg"

    with open(installed_opts_cfg, "w") as configfile:
        newconfig.write(configfile)

    if (sys.argv[1] == "install"):
        print("\n============================\n")
        print("   Successfully built F90Tree\n")
        print("============================\n")

if __name__ == "__main__":
    run_setup()

