#!/bin/sh -p
#
# Simple script to un-install F90Tree
#

if [ $# -lt 1 ]; then
   echo
   echo "Usage:"
   echo
   echo "    uninstall.sh <version> [pip_exe]"
   echo
   echo "    <version> is an integer specifying what version of python to use"
   echo "        can be one of the following"
   echo "                 2          (default)"
   echo "                 3"
   echo
   echo "    [pip_exe] is the pip executable to use"
   echo "        if version==2, defaults to pip"
   echo "        if version==3, defaults to pip3"
   echo
   echo "Examples:"
   echo
   echo "   Python 2 (default)"
   echo "      ./bin/uninstall.sh 2"
   echo "      ../bin/uninstall.sh 2 pip2.7"
   echo "      \$F90TreeDir/bin/uninstall.sh 3 pip3"
   echo
   echo "   Python 3"
   echo "      \$F90TreeDir/bin/uninstall.sh 3"
   echo "      ./bin/uninstall.sh 3 pip3"
   echo "      ./bin/uninstall.sh 3 pip   # sometimes pip gives a python 3 environment"
   echo
   
else
   cwd=`pwd`
   version=$1
   if [ $# -lt 2 ]; then # exe not given
      if [ "$version" = "2" ]; then
         pip_exe=pip
      else
         if [ "$version" = "3" ]; then
            pip_exe=pip3
         else
            echo -e "\n---ERROR: unrecognized version = "$version", expected either 2 or 3\n"
            exit
         fi
      fi
   else
      pip_exe=$2
   fi
   if [ "$version" = "2" ]; then
      installed_txt="installed_py2.txt"
      installed_options="__installed_options_py2.cfg"
   else
      installed_txt="installed_py3.txt"
      installed_options="__installed_options_py3.cfg"
   fi
   cd ${F90TreeDir}
   echo -e "\nUn-installing F90Tree..."
   echo -e "\tremove installed dependencies"
   cat ${installed_txt} | xargs rm -rf
   echo -e "\tremove local build directory"
   rm -rf build
   echo -e "\tremove local dist directory"
   rm -rf dist
   echo -e "\tremove local egg directory"
   rm -rf F90Tree.egg-info
   echo -e "\tremove installed.txt record"
   rm -f  ${installed_txt}
   echo -e "\tremove __installed_options.cfg"
   rm -f  ${installed_options}
   echo -e "\tremove installed egg directory using pip"
   yes | ${pip_exe} uninstall F90Tree
   echo -e "\nF90Tree was uninstalled\n"
   cd ${cwd}
fi

