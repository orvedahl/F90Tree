import config

# extract some build information
__name__        = config.get("installed-options", "name")
__version__     = config.get("installed-options", "version")
__author__      = config.get("installed-options", "author")
__description__ = config.get("installed-options", "description")
__pyversion__   = config.get("installed-options", "python_version")
__directory__   = config.get("installed-options", "install_directory")
__buildtime__   = config.get("installed-options", "build_time")

def info():
    print("\nPackage name = {}, version = {}\n".format(__name__, __version__))
    print(  "      Author = {}\n".format(__author__))
    print(  " Description = {}\n".format(__description__))
    print("\tPython version  --- {}".format(__pyversion__))
    print("\tBuild directory --- {}".format(__directory__))
    print("\tBuild date/time --- {}".format(__buildtime__))
    print()

