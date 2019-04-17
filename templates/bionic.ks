# Load the minimal server preseed off cdrom
preseed preseed/file=/cdrom/preseed/ubuntu-server-minimalvm.seed

# System language
lang en_US

# Language modules to install
langsupport en_US

# System keyboard
keyboard en

# System mouse
mouse

# System timezone
timezone --utc Europe/Berlin

# Root password
rootpw --disabled

# Initial user (will have sudo so no need for root)
user wikiuser --fullname "wikiuser" --password wikipass

# Reboot after installation
reboot

# Use text mode install
text

# Install OS instead of upgrade
install

# Installation media
cdrom

# Ignore errors about unmounting current drive (happens if reinstalling)
# BUG: this just seems to default the selection to yes?
# Both without owner:
#preseed partman/unmount_active boolean true
# And with owner:
#preseed --owner partman-base partman/unmount_active boolean true
# When I run the debconf-get-selections --installer it shows the owner as unknown

# System bootloader configuration
bootloader --location=mbr

# Clear the Master Boot Record
zerombr yes

# Partition clearing information
clearpart --all --initlabel

preseed partman-auto-lvm/guided_size string 10240MB
part swap --size=1024
part / --fstype=ext4 --size=9216 --grow

# Don't install recommended items by default
#preseed base-installer/install-recommends boolean false

# System authorization infomation
# The enablemd5 has to be there although it will still use salted sha256
auth  --useshadow  --enablemd5

# Network information
network --bootproto=dhcp --device=eth0

# Firewall configuration
#firewall --disabled --trust=eth0 --ssh

# Policy for applying updates. May be "none" (no automatic updates),
# "unattended-upgrades" (install security updates automatically), or
# "landscape" (manage system with Landscape).
preseed pkgsel/update-policy select unattended-upgrades

# Do not configure the X Window System
skipx
