# vbox_auto_install
Setup a Linux distro directly for VirtualBox from iso without changing anything (aka "look ma, no hands").

Take a look at the example - we assume there is an ubuntu xenial image downloaded and saved to your "distros"-folder (if not we just download it).

Only for Windows hosts for now but should easily be adapted for Linux.

If you like to contribute take a look at the TODO-file. Pull requests welcome.

# Usage & Installation
1. Install [Virtualbox](https://www.virtualbox.org/wiki/Downloads)
1. Install Python (either via [anaconda](https://www.anaconda.com/download/) or directly from [the Python download site](https://www.python.org/downloads/) )
1. Configure the .yml file in the config-folder.
1. Run install.bat or install.sh (will install pyvirtualbox and run the python scripts that will setup all VirtualBox instances in your config-folder)
