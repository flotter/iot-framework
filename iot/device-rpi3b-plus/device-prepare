#!/bin/bash

### DEFINES ###

USER=`whoami`
CPWD="$( cd "$(dirname "$0")" ; pwd -P )"

P_RESET="\e[0m"
P_RED="\e[31m"
P_YELLOW="\e[33m"

### MACROS ###

run() {
        if $VERBOSE; then
                v=$(exec 2>&1 && set -x && set -- "$@")
                echo "#${v#*--}"
                "$@"
        else
                "$@" >/dev/null 2>&1
        fi
}

function pl() {
	echo -e "$P_RESET"
}

function pn() {
	echo -e "$P_RESET$@"
}

function pr() {
	echo -e "$P_RED$@$P_RESET"
}

function py() {
	echo -e "$P_YELLOW$@$P_RESET"
}

function pnn() {
	echo -ne "$P_RESET$@"
}

function prn() {
	echo -ne "$P_RED$@$P_RESET"
}

function pyn() {
	echo -ne "$P_YELLOW$@$P_RESET"
}

function exitbuild() {
	if [ "x$SOURCED" == "x1" ]; then
		return 1
	else
		exit 1
	fi
}


CONFIG_USR=/boot/firmware/usercfg.txt
CONFIG_SYS=/boot/firmware/syscfg.txt
CONFIG_CMD=/boot/firmware/cmdline.txt

py "Running Natively"
pl

source $CPWD/native-input

VERBOSE=$GEN_VERBOSE

if [ "x$VERBOSE" == "xtrue" ]; then
	cat $CPWD/native-input
	pl
fi

if [ "x$GEN_PRODUCTION" == "xtrue" ]; then
        pnn "- Image type : "
	py "RELEASE/PRODUCTION"
	
	# System Cfg
	echo "### RPI3B ###" > $CONFIG_SYS
	echo "enable_uart=0" >> $CONFIG_SYS

	# User Cfg
	echo "### RPI3B ###" > $CONFIG_USR
	echo "" >> $CONFIG_USR
	echo "dtoverlay=disable-bt" >> $CONFIG_USR
	run systemctl disable hciuart.service
	run systemctl disable bluealsa.service
	run systemctl disable bluetooth.service

	pnn "- Disabling Bluetooth : "
	py "OK"
	pnn "- Disabling UARTs : "
	py "OK"
	pnn "- Disabling SSHD : "
	py "OK"
else
	pnn "- Image type : "
	py "DEBUG"
	
	# System Cfg
	echo "### RPI3B ###" > $CONFIG_SYS
	echo "enable_uart=1" >> $CONFIG_SYS

	# User Cfg
	echo "### RPI3B ###" > $CONFIG_USR
	echo "" >> $CONFIG_USR 
	echo "dtoverlay=disable-bt" >> $CONFIG_USR
	run systemctl disable hciuart.service
	run systemctl disable bluealsa.service
	run systemctl disable bluetooth.service
	
	pnn "- Disabling Bluetooth : "
	py "OK"
	pnn "- Enabling UARTs : "
	py "OK"
	pnn "- Enabling SSHD : "
	touch /boot/firmware/ssh
	py "OK"
fi

pnn "- Add FSCK on every boot : "
echo "$(cat $CONFIG_CMD) fsck.mode=force fsck.repair=yes" > $CONFIG_CMD
py "DONE"

pnn "- Override flash-kernel for chroot : "
echo "Raspberry Pi 3 Model B Plus Rev 1.3" > /etc/flash-kernel/machine
py "DONE"

pnn "- Disable Auto Resize on boot : "
run rm -rf /etc/init.d/resize2fs_once
py "DONE"

pnn "- Changing Locale : "
export LANG="en_US.UTF-8"
export LANGUAGE="en_US:en"
echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen
run locale-gen
run dpkg-reconfigure -f noninteractive locales
py "OK"

pnn "- Cloud Init User Config : "
run cp -f $CPWD/native-prepare/user-data /boot/firmware
py "OK"

pnn "- Update APT : "
run apt -y remove needrestart
run apt-get update
run apt-get -y dist-upgrade
run apt remove -y unattended-upgrades
py "OK"

pnn "- Installing components : "
run apt-get install -y build-essential vim nano cryptsetup python3-distutils iw wget fake-hwclock ntpdate libasound2-plugins libraspberrypi-bin wireless-tools
run apt-get install -y python3-pip
run python3 -m pip install --upgrade pip
run python3 -m pip install s3cmd
py "OK"

pnn "- Creating /tmp based on RAM : "
run mkdir -p /tmp
py "DONE"

pnn "- Disable Snapd : "
run apt-get purge -y snapd
py "DONE"

pnn "- Compiling and installing xkey : "
run gcc $CPWD/native-prepare/xkey.c -o $CPWD/native-prepare/xkey
run chmod +x $CPWD/native-prepare/xkey
run cp $CPWD/native-prepare/xkey /bin
py "DONE"

pnn "- Installing encrypted drive service : "
run cp $CPWD/native-prepare/player-hw-test /bin/
run cp $CPWD/native-prepare/crypt-commission-start /bin/
run cp $CPWD/native-prepare/crypt-commission-end /bin/
run cp $CPWD/native-prepare/check-update /bin/
run cp $CPWD/native-prepare/led-control /bin/
run cp $CPWD/native-prepare/online-update /bin/
run cp $CPWD/native-prepare/online-version /bin/
run cp $CPWD/native-prepare/offline-version /bin/
run cp $CPWD/native-prepare/*.service /etc/systemd/system
run systemctl enable cryptkey
run systemctl enable ep
run systemctl enable check-update
run systemctl enable ep-update
run systemctl enable hw-update
py "DONE"

pnn "- Disable WPA Supplicant Service : "
run systemctl disable wpa_supplicant.service
py "DONE"

pnn "- Systemd Network Online Wait Dropin Mod : "
mkdir -p /etc/systemd/system/systemd-networkd-wait-online.service.d/
echo "[Service]" > /etc/systemd/system/systemd-networkd-wait-online.service.d/override.conf
echo "ExecStart=" >> /etc/systemd/system/systemd-networkd-wait-online.service.d/override.conf
echo "ExecStart=/lib/systemd/systemd-networkd-wait-online --any" >> /etc/systemd/system/systemd-networkd-wait-online.service.d/override.conf
py "OK"

pnn "- Refresh SO libraries : "
run ldconfig
py "DONE"

pnn "- Insert Version Metadata : "
echo "VERSION:$GEN_VERSION" > $CPWD/.build-meta
echo "DATE:$GEN_DATE" >> $CPWD/.build-meta
echo "PRODUCTION:$GEN_PRODUCTION" >> $CPWD/.build-meta
py "DONE"

if [ "x$GEN_INTERACTIVE" == "xtrue" ]; then
	pl
	py "[INPECTION POINT] Interactive terminal (type 'exit' to finish) : "
	pl
	bash
	pl
fi

pnn "- Remove flash-kernel override for chroot : "
run rm -rf /etc/flash-kernel/machine
py "DONE"
