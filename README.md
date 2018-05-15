# vbox_auto_install
Setup a Linux distro directly for VirtualBox from iso without changing anything (aka "look ma, no hands").

Take a look at the example - we assume there is an ubuntu xenial image downloaded and saved to your "distros"-folder (if not we just download it).

Only for Windows hosts for now but should easily be adapted for Linux.

If you like to contribute take a look at the TODO-file. Pull requests welcome.

# Usage & Installation
1. install Virtualbox
1. install Python
1. download the sdk from https://www.virtualbox.org/wiki/Downloads
1. Unzip the archive and run the vboxapisetup.py file using your system Python with the following command: `python vboxapisetup.py install`
1. configure setup.json
1. run install_xenial_virtualbox.bat (will install pyvirtualbox and run the python script)
