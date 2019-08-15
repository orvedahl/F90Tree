#!/bin/sh -p
#
# Simple script to install F90Tree
#

if [ $# -lt 1 ]; then
   echo
   echo "Usage:"
   echo
   echo "    install.sh <version> [python-exe]"
   echo
   echo "    <version> is an integer specifying what version of python to use"
   echo "        can be one of the following"
   echo "                 2          (default)"
   echo "                 3"
   echo
   echo "    [python-exe] is the python executable that will be used"
   echo "        if version==2, defaults to python"
   echo "        if version==3, defaults to python3"
   echo
   echo "Examples:"
   echo
   echo "   Python 2 (default)"
   echo "      ./bin/install.sh 2"
   echo "      ../bin/install.sh 2 python2.7"
   echo "      \$F90TreeDir/bin/install.sh 3 python3"
   echo
   echo "   Python 3"
   echo "      \$F90TreeDir/bin/install.sh 3"
   echo "      ./bin/install.sh 3 python3"
   echo "      ./bin/install.sh 3 python   # sometimes python gives a python 3 environment"
   echo
else
   cwd=`pwd`
   version=$1
   if [ $# -lt 2 ]; then # exe not given
      if [ "$version" = "2" ]; then
         python_exe=python
      else
         if [ "$version" = "3" ]; then
            python_exe=python3
         else
            echo -e "\n---ERROR: unrecognized version = "$version", expected either 2 or 3\n"
            exit
         fi
      fi
   else
      python_exe=$2
   fi
   if [ "$version" = "2" ]; then
      installed_txt="installed_py2.txt"
   else
      installed_txt="installed_py3.txt"
   fi
   cd ${F90TreeDir}
   echo -e "\nInstalling F90Tree...\n"
   ${python_exe} setup.py build
   ${python_exe} setup.py install --user --record ${installed_txt}
   cd ${cwd}
fi

