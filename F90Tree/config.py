"""
Read the various configuration files

Examples
--------
>>> import F90Tree as FT
>>> C = FT.config
>>>
>>> value = C.get("section-name", "string-variable-name")
>>> type(value)
<type 'str'>
>>>
>>> value = C.getboolean("section-name", "bool-variable-name")
>>> type(value)
<type 'bool'>
>>>
>>> value = C.getint("section-name", "int-variable-name")
>>> type(value)
<type 'int'>
>>>
>>> value = C.getfloat("section-name", "float-variable-name")
>>> type(value)
<type 'float'>
"""

import os
import sys

if (sys.version_info[0] == 2):
    # using Python 2
    from ConfigParser import ConfigParser
    installed_opts_cfg = "__installed_options_py2.cfg"
else:
    # using Python 3
    from configparser import ConfigParser
    installed_opts_cfg = "__installed_options_py3.cfg"

F90TreeDir = os.environ['F90TreeDir']

# create configuration file object
config = ConfigParser()

# read defaults from installation directory
config.read(os.path.join(F90TreeDir, 'f90tree.cfg'))

# read defaults from user's home directory
config.read(os.path.expanduser('~/.f90tree/f90tree.cfg'))

# read defaults from local directory
config.read('f90tree.cfg')

# override any issues that the installation process detected
config.read(os.path.join(F90TreeDir, installed_opts_cfg))

